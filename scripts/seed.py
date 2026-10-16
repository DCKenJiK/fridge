import subprocess

items = [
    ("beef stew", "beef", "freezer", "Makes 3 portions"),
    ("chicken pad thai", "chicken", "freezer", "3 servings"),
    ("lasagna", "beef", "freezer", "Freeze in individual portions"),
    ("fish tacos", "fish", "freezer", "With tortillas"),
    ("veggie burritos", "vegetarian", "freezer", "4 pack"),
    ("chicken stir fry", "chicken", "freezer", ""),
    ("beef stroganoff", "beef", "freezer", ""),
    ("pork chops", "pork", "freezer", ""),
    ("chocolate cake", "dessert", "freezer", "Birthday leftover"),
    ("marinara sauce", "sauce", "freezer", "Makes 2 cups"),
    ("basil pesto", "pesto", "freezer", "Homemade"),
    ("tomato basil soup", "tomato_sauce", "freezer", "3 servings"),
    ("beef chili", "beef", "freezer", "Doubly good recipe"),
    ("chicken tikka masala", "chicken", "freezer", ""),
    ("pork tenderloin", "pork", "freezer", "Vacuum sealed"),
    ("salmon fillet", "fish", "freezer", "2 pieces"),
    ("margherita pizza", "vegetarian", "freezer", "Homemade"),
    ("brownies", "dessert", "freezer", "Baked last week"),
    ("chicken alfredo", "chicken", "freezer", "Pasta dish"),
    ("beef brisket", "beef", "freezer", "Sunday roast"),
    ("frozen pancakes", "breakfast", "freezer", "Weekend batch"),
    ("french toast casserole", "breakfast", "freezer", "Holiday leftover"),
    ("overnight oats", "breakfast", "fridge", "Makes 2 jars"),
    ("hardboiled eggs", "breakfast", "fridge", "5 eggs"),
    ("bacon, cooked", "breakfast", "fridge", "Freeze in 4-pack"),
    ("waffles", "breakfast", "freezer", "Box waffles"),
    ("muffins", "breakfast", "freezer", "Blueberry, 6 pack"),
    ("banana bread", "breakfast", "freezer", "Sliced"),
    ("hash browns", "breakfast", "freezer", "Shredded, frozen"),
    ("breakfast burritos", "breakfast", "freezer", "Make ahead, 6 count"),
    ("sausage links", "breakfast", "freezer", "Bulk pack, separate"),
    ("pasta sauce", "tomato_sauce", "freezer", "Jarred, 2 cups"),
    ("chicken soup", "chicken", "freezer", "Homemade, 4 servings"),
    ("ground beef, cooked", "beef", "freezer", "For tacos or pasta"),
    ("shrimp, frozen", "fish", "freezer", "Peeled, 1 lb"),
    ("tofu stir fry", "vegetarian", "freezer", "Pre-portioned"),
    ("corn on the cob", "vegetarian", "freezer", "Boiled, buttered"),
    ("ribs", "pork", "freezer", "Baby back, 1 rack"),
    ("turkey breast", "chicken", "freezer", "Leftover thanksgiving"),
    ("mango sorbet", "dessert", "freezer", "Homemade"),
    ("apple pie", "dessert", "freezer", "Whole pie, sliced available"),
    ("rice, cooked", "other", "freezer", "Leftover rice, frozen"),
    ("dumplings", "vegetarian", "freezer", "24 count, frozen"),
    ("ice cream", "dessert", "freezer", "Half gallon tub"),
    ("pizza dough", "other", "freezer", "Makes 2 pizzas"),
    ("chicken wings", "chicken", "freezer", "Frozen, 2 lbs"),
    ("beef broth", "sauce", "freezer", "Makes 4 cups"),
    ("zucchini bread", "breakfast", "freezer", "Sliced, homemade"),
    ("pork carnitas", "pork", "freezer", "Slow cooker leftover"),
    ("spinach quiche", "breakfast", "freezer", "Quarter slices, 4 count"),
]

for name, cat, storage, notes in items:
    cmd = ["fridge", "add", name, "--category", cat, "--storage", storage]
    if notes:
        cmd.extend(["--notes", notes])
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.stderr:
        print(f"  STDERR: {r.stderr.strip()}")

