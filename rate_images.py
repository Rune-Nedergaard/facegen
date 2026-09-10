import os
import random
import pandas as pd
import streamlit as st

FOLDER = r"/Users/fredhb/Desktop/DTU_projects/Kareninator-keerthi/data/preprocessed_data"
RANDOM_SEED = 22

# ---- init ----
if "images" not in st.session_state:
    paths = [os.path.join(FOLDER, f) for f in os.listdir(FOLDER)]
    valid = [p for p in paths if os.path.splitext(p)[1].lower() in {".jpg",".jpeg",".png",".webp",".bmp"}]
    # duplicate each image once
    doubled = valid * 2
    random.Random(RANDOM_SEED).shuffle(doubled)
    st.session_state.images = doubled

if "counter" not in st.session_state:
    st.session_state.counter = 0
if "ratings" not in st.session_state:
    # list of dicts so we can store multiple ratings per image
    st.session_state.ratings = []

images = st.session_state.images
if not images:
    st.error("No images found.")
    st.stop()

idx = max(0, min(st.session_state.counter, len(images)-1))
st.session_state.counter = idx
photo = images[idx]
filename = os.path.basename(photo)

col1, col2 = st.columns(2)
col1.subheader(f"{idx+1}/{len(images)}")
col1.image(photo, caption=filename, use_container_width=True)
col2.write("#")

# Unique slider key per "instance" of image (filename + position in list)
slider_key = f"rating_{idx}_{filename}"

# If the slider key hasn't been created before, pre-seed it with 0
if slider_key not in st.session_state:
    st.session_state[slider_key] = 1

rating = col2.slider("Rating (1–5)", 1, 5, key=slider_key)
col2.caption("Use the slider, then click a button below.")

# Save & Next
if col2.button("Save rating & next ⏭️"):
    st.session_state.ratings.append({"Image": filename, "Rating": int(rating)})
    if st.session_state.counter < len(images) - 1:
        st.session_state.counter += 1
        st.rerun()
    else:
        st.success("You have rated all images twice. 🎉")

# Back
if col2.button("⬅️ Back"):
    if st.session_state.counter > 0:
        st.session_state.counter -= 1
        st.rerun()

# Table + download
rating_df = pd.DataFrame(st.session_state.ratings)
st.divider()
st.dataframe(rating_df, use_container_width=True)
st.download_button(
    "⬇️ Download CSV",
    data=rating_df.to_csv(index=False).encode("utf-8"),
    file_name="image_ratings.csv",
    mime="text/csv"
)