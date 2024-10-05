### Which foods are served at Italian restaurants?
```
SELECT FoodItem.name
FROM FoodItem
JOIN Menu ON FoodItem.foodId = Menu.foodId
JOIN Restaurants ON Menu.restaurantId = Restaurants.restaurantId
WHERE Restaurants.cuisine = 'Italian';
```
Italian restaurants typically serve spaghetti, soup, olive pizza, and tiramisu.


### How big is the menu at Olive Garden?
```
SELECT COUNT(foodId) FROM Menu WHERE restaurantId = (SELECT restaurantId FROM Restaurants WHERE name = 'Olive Garden');
```
There are 2 items in the menu at Olive Garden.


### Which restaurant has the least amount of choices?
```
SELECT r.name AS restaurant_name 
FROM Restaurants r 
JOIN Menu m ON r.restaurantId = m.restaurantId 
GROUP BY r.restaurantId, r.name 
ORDER BY COUNT(m.foodId) ASC 
LIMIT 1;
```
The restaurant with the least amount of choices is "Papa John's" with only 1 food item on its menu.


### Who is the head chef at olive garden?
```
SELECT name
FROM FoodItem;
```
The response does not provide any information on who the head chef at Olive Garden is.


### Are there more Italian or Belgian restaurants?
```
SELECT cuisine, COUNT(restaurantId) AS num_restaurants
FROM Restaurants
WHERE cuisine IN ('Italian', 'Belgian')
GROUP BY cuisine;
```
There are more Italian restaurants than Belgian restaurants.


### Which restaurants don't serve 2 or more vegetarian options?
```
SELECT r.name AS restaurant_name
FROM Restaurants r
WHERE r.restaurantId NOT IN (
    SELECT m.restaurantId
    FROM Menu m
    JOIN FoodItem fi ON m.foodId = fi.foodId
    WHERE fi.vegetarian = TRUE
    GROUP BY m.restaurantId
    HAVING COUNT(m.foodId) >= 2
);
```
The restaurants Olive Garden, Papa Johns, Taco Bell, Bruges, Del Taco, and Carls Jr do not serve 2 or more vegetarian options.
