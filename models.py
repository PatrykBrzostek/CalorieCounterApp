from calories_calculator import Calculator
from peewee import *
from datetime import date
import os
import sys
from exeptions import *

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class Meal(Model):
    ean = CharField(unique=True)
    name = CharField()
    carbohydrates = FloatField()
    proteins = FloatField()
    fats = FloatField()

    class Meta:
        database = db

class Day(Model):
    date = DateField(default=date.today())
    meal = ForeignKeyField(Meal)
    weight = FloatField()

    class Meta:
        database = db


class DatabaseOpener():
    '''
    The context menager, which connects to passed database and closes it.
    '''
    def __init__(self, database):
        self.db=database

    def __enter__(self):
        try:
            self.db.connect()
        except:
            print('Could not connect to database')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()



class DatabaseOperator(): #class name to confirm
    def __init__(self, database, database_filename):
        self.calculator=Calculator()
        self.database=database
        self.database_filename=database_filename
        if os.path.isfile(self.database_filename):
            self.database.init(self.database_filename)
        else:
            # structure of this condition is necessary to avoid creating the same tables on existing databases
            self.database.init(self.database_filename)
            try:
                with DatabaseOpener(self.database):
                    self.database.create_tables([Meal, Day])
            except:
                print('Execution terminated')
                sys.exit()

    def add_meal_to_database(self, args):
        print('Added a meal to database')
        print(args.name, args.carbohydrates, args.proteins, args.ean)

        if Meal.filter(Meal.ean==args.ean):#make your exeption
            raise CCAppUniqueItemException('The EAN number: {} is already in the database'.format(args.ean))
        elif args.carbohydrates+args.proteins+args.fats>args.weight:
            raise CCAppValueErrorException('The sum of macronutriens is bigger than weight of a meal.')
        else:
            if args.weight!=100:
                c,p,f=self.calculator.get_macro_per_100gram(args.carbohydrates,args.proteins,args.fats,args.weight)
            else:
                c,p,f=args.carbohydrates,args.proteins,args.fats
            Meal.create(name=args.name, ean=args.ean, carbohydrates=c, proteins=p, fats=f)

            # day1=Day(date=date.today(),weight=150, meal=Meal.get(Meal.name == 'soup'))
            # day2=Day(date=date.today(),weight=150, meal=Meal.get(Meal.name == 'soup'))
            # print(day1.meal.name, day1.meal.ean)

    def add_meal(self,args):
        macro = [args.carbohydrates, args.proteins, args.fats]

        if args.ean.isdigit(): #if user entered the ean number
            if Meal.filter(Meal.ean == args.ean):
                pass
            else:
                macro=[.0 if i is None else i for i in macro]
                Meal.create(name=args.name, ean=args.ean, carbohydrates=macro[0], proteins=macro[1], fats=macro[2])
        else:
            if all(i is None for i in macro):
                raise CCAppValueErrorException('At least one of the macronutrients has to have defined value.')
            else:
                macro=[.0 if i is None else i for i in macro]
                Meal.create(name=args.name, ean=args.ean, carbohydrates=macro[0], proteins=macro[1], fats=macro[2])

        Day.create(meal=Meal.get(Meal.ean == args.ean), weight=args.weight)
        #dodaj wybor daty, ale z zabezpieczeniem, ze nie wprzód
        #przeanalizuj logike czy nie ma bledow

    def temp(self,args):
        for day in Day.select():
            print(day.date, day.meal.ean, day.weight)


