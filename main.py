import argparse
import psycopg2
from chatGPT import ask_chatgpt


def main():
    parser = argparse.ArgumentParser(description='Handle connection string input')

    # Argument gets passed in as: """ -c="Your URL HERE" """
    parser.add_argument('-c', type=str, required=True,
                        help='connection string for database')
    parser.add_argument('-k', type=str, required=True,
                        help='key for open ai')

    args = parser.parse_args()
    connectionString = args.c
    openAiSecretKey = args.k

    ask_chatgpt("Why is the sky blue?", openAiSecretKey)

    dropMenuTable = """
    DROP TABLE IF EXISTS Menu;
    """

    dropRestaurantsTable = """
    DROP TABLE IF EXISTS Restaurants;
    """

    dropFoodItemTable = """
    DROP TABLE IF EXISTS FoodItem;
    """

    createFoodItemTable = """
    CREATE TABLE IF NOT EXISTS FoodItem (
        foodId SERIAL PRIMARY KEY,
        name VARCHAR(45) NOT NULL UNIQUE,
        vegetarian BOOLEAN DEFAULT FALSE
    );
    """

    createRestaurantTable = """
    CREATE TABLE IF NOT EXISTS Restaurants (
        restaurantId SERIAL PRIMARY KEY,
        name VARCHAR(45) NOT NULL,
        cuisine VARCHAR(45)
    );
    """

    createMenuTable = """
    CREATE TABLE IF NOT EXISTS Menu (
        restaurantId INTEGER NOT NULL,
        foodId INTEGER NOT NULL,
        PRIMARY KEY (restaurantId, foodId),
        FOREIGN KEY (foodId) REFERENCES FoodItem (foodId) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (restaurantId) REFERENCES Restaurants (restaurantId) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """

    insert_restaurants = """
      INSERT INTO Restaurants (name, cuisine)
      VALUES (%s, %s)
    """

    default_restaurants = [
        ("Olive Garden", "Italian"),
        ("Papa Johns", "American"),
        ("Taco Bell", "Mexican"),
        ("Bruges", "Belgian"),
        ("Del Taco", "Mexican"),
        ("Buco De Peppo", "Italian"),
        ("Carls Jr", "Armerican"),
    ]

    with psycopg2.connect(connectionString) as conn:
        cursor = conn.cursor()
        # Drop things so we get a fresh start
        cursor.execute(dropMenuTable)
        cursor.execute(dropRestaurantsTable)
        cursor.execute(dropFoodItemTable)
        # Now make them again! Yay!
        cursor.execute(createFoodItemTable)
        cursor.execute(createRestaurantTable)
        cursor.execute(createMenuTable)
        cursor.executemany(insert_restaurants, default_restaurants)
        cursor.execute("SELECT * FROM restaurants")
        result = cursor.fetchall()
        conn.commit()

    for row in result:
        print(row)


if __name__ == '__main__':
    main()