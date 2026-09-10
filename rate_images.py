import os
import random

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(BASE_DIR, "subset_300_white_men_20_35")
RANDOM_SEED = 22


def get_valid_images():
    paths = [os.path.join(FOLDER, name) for name in os.listdir(FOLDER)]
    valid = [
        path for path in paths
        if os.path.splitext(path)[1].lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    ]
    return sorted(valid)


def current_participant_name():
    return st.session_state.get("participant", "Group member 1")


def participant_csv_name(participant_name):
    return f"{participant_name.lower().replace(' ', '_')}.csv"


def count_occurrences_seen(filename):
    seen = 0
    for path in st.session_state.images[: st.session_state.counter + 1]:
        if os.path.basename(path) == filename:
            seen += 1
    return seen


def save_participant_csv(participant_name):
    participant_ratings = st.session_state.ratings_by_participant.get(participant_name, {})
    rows = list(participant_ratings.values())
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[["Image", "Rating 1", "Rating 2"]]
    else:
        df = pd.DataFrame(columns=["Image", "Rating 1", "Rating 2"])

    csv_path = os.path.join(BASE_DIR, participant_csv_name(participant_name))
    df.to_csv(csv_path, index=False)
    return df


def advance_image():
    images = st.session_state.images
    if st.session_state.counter < len(images) - 1:
        st.session_state.counter += 1
        st.rerun()
    else:
        st.success("You have rated all images twice. 🎉")


def record_rating(rating_value):
    images = st.session_state.images
    if not images:
        return

    filename = os.path.basename(images[st.session_state.counter])
    participant_name = current_participant_name()
    ratings = st.session_state.ratings_by_participant.setdefault(participant_name, {})
    row = ratings.setdefault(filename, {"Image": filename, "Rating 1": None, "Rating 2": None})

    occurrence_num = count_occurrences_seen(filename)
    if occurrence_num == 1:
        row["Rating 1"] = int(rating_value)
    else:
        row["Rating 2"] = int(rating_value)

    st.session_state.ratings_by_participant[participant_name] = ratings
    save_participant_csv(participant_name)
    advance_image()


def discard_current_image():
    images = st.session_state.images
    if not images:
        return

    filename = os.path.basename(images[st.session_state.counter])
    participant_name = current_participant_name()
    discarded = st.session_state.discarded_by_participant.setdefault(participant_name, [])
    if filename not in discarded:
        discarded.append(filename)
    st.session_state.discarded_by_participant[participant_name] = discarded
    advance_image()


# ---- init ----
if "images" not in st.session_state:
    valid = get_valid_images()
    if valid:
        image_order = valid * 2
        random.Random(RANDOM_SEED).shuffle(image_order)
        st.session_state.images = image_order
    else:
        st.session_state.images = []

if "counter" not in st.session_state:
    st.session_state.counter = 0
if "participant" not in st.session_state:
    st.session_state.participant = "Group member 1"
if "ratings_by_participant" not in st.session_state:
    st.session_state.ratings_by_participant = {
        "Group member 1": {},
        "Group member 2": {},
    }
if "discarded_by_participant" not in st.session_state:
    st.session_state.discarded_by_participant = {
        "Group member 1": [],
        "Group member 2": [],
    }
st.title("Image rating task")


def keyboard_listener():
    return components.html(
        """
        <script>
        addEventListener("keydown", e => {
          if (["1","2","3","4","5","6"].includes(e.key)) {
            e.preventDefault();
            Streamlit.setComponentValue(e.key);
          }
        });
        </script>
        """,
        height=0,
    )


key = keyboard_listener()
if key:
    if key == "6":
        discard_current_image()
    elif key in {"1", "2", "3", "4", "5"}:
        record_rating(int(key))

images = st.session_state.images
if not images:
    st.error("No images found.")
    st.stop()

idx = max(0, min(st.session_state.counter, len(images) - 1))
st.session_state.counter = idx
photo = images[idx]
filename = os.path.basename(photo)

st.caption(f"Selected participant: {current_participant_name()}")
col_participant_1, col_participant_2 = st.columns(2)
if col_participant_1.button("Group member 1"):
    st.session_state.participant = "Group member 1"
if col_participant_2.button("Group member 2"):
    st.session_state.participant = "Group member 2"

col1, col2 = st.columns(2)
col1.subheader(f"{idx + 1}/{len(images)}")
col1.image(photo, use_container_width=True)
col2.write("#")

rating = col2.slider("Rating (1–5)", 1, 5, key="rating_slider")
col2.caption("Use the mouse or press 1–5 on the keyboard. Press 6 to discard the image.")

if col2.button("Save rating & next ⏭️"):
    record_rating(int(rating))

if col2.button("Discard image 🚫"):
    discard_current_image()

if col2.button("⬅️ Back"):
    if st.session_state.counter > 0:
        st.session_state.counter -= 1
        st.rerun()

current_participant = current_participant_name()
current_df = pd.DataFrame(
    list(st.session_state.ratings_by_participant.get(current_participant, {}).values())
)
if not current_df.empty:
    current_df = current_df[["Image", "Rating 1", "Rating 2"]]
else:
    current_df = pd.DataFrame(columns=["Image", "Rating 1", "Rating 2"])

st.divider()
st.subheader(f"Ratings for {current_participant}")
st.dataframe(current_df, use_container_width=True)
st.download_button(
    "⬇️ Download current participant CSV",
    data=current_df.to_csv(index=False).encode("utf-8"),
    file_name=participant_csv_name(current_participant),
    mime="text/csv",
)

current_discarded = st.session_state.discarded_by_participant.get(current_participant, [])
if current_discarded:
    st.caption(f"Discarded images: {', '.join(current_discarded)}")