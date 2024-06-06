# Define the mapping of animals, their locations, an interesting fact, and a hint
animal_questions = {
    "Giraffe": ("Africa", "Did you know that giraffes have the same number of neck vertebrae as humans, despite their long necks?", "It's the continent with the famous Serengeti."),
    "Panda": ("Asia", "Pandas spend around 14 hours a day eating bamboo.", "It's the largest continent in the world."),
    "Kangaroo": ("Australia", "Kangaroos can leap over 30 feet in a single bound.", "It's known as the 'Land Down Under'."),
    "Penguin": ("Antarctica", "Penguins can drink seawater because they have a special gland that filters out the salt.", "It's the coldest continent."),
    "Elephant": ("Africa", "Elephants are the largest land animals and can weigh up to 14,000 pounds.", "It's home to the Sahara Desert."),
    "Tiger": ("Asia", "Tigers are excellent swimmers and can swim for several kilometers.", "It's the continent with the Great Wall."),
    "Koala": ("Australia", "Koalas sleep up to 18 hours a day to conserve energy.", "It's the smallest continent."),
    "Polar Bear": ("Arctic", "Polar bears have black skin under their white fur to absorb heat from the sun.", "It's the northernmost region.")
}

# Define the mapping of continent Aruco card IDs to continent names
continent_cards = {
    1: "Africa",
    2: "Asia",
    3: "Australia",
    4: "Antarctica",
    5: "Arctic"
}

correct_responses = [
    "Well done! The {animal} indeed lives in {location}.",
    "Great job! You found that the {animal} is from {location}.",
    "Excellent! The {animal} calls {location} its home.",
    "You're right! The {animal} lives in {location}.",
    "Good work! The {animal} is indeed found in {location}."
]

incorrect_responses = [
    "That's not the right answer. Try again!",
    "Not quite. Give it another shot! You can do it!",
    "That's incorrect. Please try once more!",
    "Nope, that's not it. Try again!",
    "That's not the right one. But have another go!"
]