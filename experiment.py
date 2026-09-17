from psychopy import visual, core, event
import os
import random

# --------------------------
# SETTINGS
# --------------------------
ADAPTOR_FOLDER = "adaptors"
TEST_FOLDER = "test_images"

ADAPTOR_TIME = 20      # seconds
TEST_TIME = 1        # seconds

# --------------------------
# LOAD IMAGE FILES
# --------------------------
valid_exts = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

adaptor_images = [
    os.path.join(ADAPTOR_FOLDER, f)
    for f in os.listdir(ADAPTOR_FOLDER)
    if f.lower().endswith(valid_exts)
]

test_images = [
    os.path.join(TEST_FOLDER, f)
    for f in os.listdir(TEST_FOLDER)
    if f.lower().endswith(valid_exts)
]

print("Adaptor images:", adaptor_images)
print("Test images:", test_images)

# --------------------------
# BUILD ALL CONDITIONS
# --------------------------
trials = []

for adaptor_path in adaptor_images:
    for test_path in test_images:
        trials.append({
            "adaptor": adaptor_path,
            "test": test_path
        })

# Shuffle trial order
random.shuffle(trials)

# --------------------------
# CREATE WINDOW
# --------------------------
win = visual.Window(size=(1000, 800), color="gray", units="pix")

fixation = visual.TextStim(
    win,
    text="+",
    color="red",
    height=30,
    pos=(0, 0)
)

# --------------------------
# BUILD ALL CONDITIONS
# Each unique combination appears 3 times
# --------------------------

trials = []

REPEATS = 3

for _ in range(REPEATS):
    for adaptor_path in adaptor_images:
        for test_path in test_images:
            trials.append({
                "adaptor": adaptor_path,
                "test": test_path
            })

# Randomize the order of all trials
random.shuffle(trials)

print(f"Total number of trials: {len(trials)}")

# --------------------------
# RUN TRIALS
# --------------------------
for i, trial in enumerate(trials, start=1):
    print(f"Trial {i}:")
    print("  Adaptor:", trial["adaptor"])
    print("  Test:", trial["test"])

    adaptor_stim = visual.ImageStim(win, image=trial["adaptor"], size=(500, 500))
    test_stim = visual.ImageStim(win, image=trial["test"], size=(500, 500))

    # Show adaptor
    adaptor_stim.draw()
    fixation.draw()
    win.flip()
    core.wait(ADAPTOR_TIME)

    # Show test
    test_stim.draw()
    fixation.draw()
    win.flip()
    core.wait(TEST_TIME)

    # Blank screen after test
    win.flip()

    # Optional short pause between trials
    core.wait(1)

    # Allow quitting with escape
    keys = event.getKeys()
    if "escape" in keys:
        break

win.close()
core.quit()