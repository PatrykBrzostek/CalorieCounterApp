# Calorie Counter App

## Idea
Calorie Counter App is a command line app, which is based on apps like Fitatu or Yazio.
The app provides the basic features: counting colories in eaten meals, adding meals to a local database, showing stats. Usage instructions are given below. 

The app is created using the following python modules: argparse, peewee, pandas.

The next step is to convert the app to a Django web app with user registration functionality.  

## Requirements
* Python 3.8
* peewee 3.14.4
* pandas 1.3.1
* argparse 1.4.0


## Usage
Clone the repo and you can run the script by one of the commands:
```bash
python main.py add-a-meal [-h] [--name NAME] [--ean EAN] [-c CARBOHYDRATES] [-p PROTEINS] [-f FATS] [-w WEIGHT] [-d DATE]
python main.py save-a-meal-in-the-database [-h] [-w WEIGHT] name ean carbohydrates proteins fats
python main.py show-today 
python main.py show-stats [-h] [--start-date START_DATE] [--end-date END_DATE]
```

* add a meal - adding a meal to given date (default today). There are few ways to use this option: you can define it by ean, if this ean is already in the database, you can type only amount of macronutriens or you can type all data of meal with ean and name, then this meal will be saved in database for future usage.
* save a meal in the database - saving a data of a meal in local database; deafult weight=100g
* show today - showing all meals and total sum of macronutriens and kcal for today's date
* show stats - showing stats (amount of macronutriens and kcal) per day for given period; default last week
## Examples of usage
Note: The default database has some temporary data, so you can try the app with this database or you can delete it and make a new one. In the future I'm going to connect my app with a external database of meals and to add user registration.

```bash
python main.py add-a-meal --ean=785
python main.py add-a-meal --ean=782 --name=mypancakes -c=40 -p=15 -f=30
python main.py add-a-meal -c=20 -p=35 -f=3.2
python main.py add-a-meal -p=40
python main.py save-a-meal-in-the-database chocolate_cream 345212 56 8 23
python main.py save-a-meal-in-the-database mysoup 12312 12 10 21 -w=50
python main.py show-today
python main.py show-stats
python main.py show-stats --start-date=2021-05-04
python main.py show-stats --start-date=2021-06-01 --end-date 2021-06-30
```

## Example outputs
```bash
        name                 ean weight  carbohydrates  proteins  fats    kcal
0      meal  N210809231200069296  100.0          100.0       0.0   0.0   400.0
1      meal  N210809231240675328  100.0          100.0       3.0  22.0   610.0
2      meal  N210809231301946207  100.0           80.0       3.2  43.2   721.6
3      meal  N210809233152096564  150.0          100.0       0.0   0.0   400.0
Total                                            380.0       6.2  65.2  2131.6
```

```bash
      date  carbohydrates  proteins  fats   kcal
2021-08-03          288.0      54.0 870.0 9198.0
2021-08-09          380.0       6.2  65.2 2131.6
2021-08-10           89.0     230.0  33.2 1574.8
```