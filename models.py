from calories_calculator import Calculator
from peewee import *
from datetime import date, datetime
import os
import sys
from exeptions import *
import pandas as pd
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

    def save_a_meal_in_the_database(self, args):
        if Meal.filter(Meal.ean==args.ean):
            raise CCAppUniqueItemException('The EAN number: {} is already in the database'.format(args.ean))
        elif args.carbohydrates+args.proteins+args.fats>args.weight:
            raise CCAppValueErrorException('The sum of macronutriens is bigger than weight of a meal.')
        else:
            if args.weight!=100:
                c,p,f=self.calculator.get_macro_per_100gram(args.carbohydrates,args.proteins,args.fats,args.weight)
            else:
                c,p,f=args.carbohydrates,args.proteins,args.fats
            Meal.create(name=args.name, ean=args.ean, carbohydrates=c, proteins=p, fats=f)


    def add_a_meal(self, args):
        macro = [args.carbohydrates, args.proteins, args.fats]

        try:
            datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            raise CCAppDataFormatException("Incorrect data format, should be YYYY-MM-DD")

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

        Day.create(date=args.date, meal=Meal.get(Meal.ean == args.ean), weight=args.weight)


    def show_today(self, args):
        today='2021-08-09'
        query = Day.select(Meal.name, Meal.ean, Day.weight, Meal.carbohydrates, Meal.proteins, Meal.fats).join(Meal).where(Day.date == today)
        df = pd.DataFrame(list(query.dicts()))
        #df.loc[3,'carbohydrates']=df.loc[3,'carbohydrates']*self.calculator.get_portions_scale(df.loc[3,'weight'])
        df['kcal']=[self.calculator.count_calories(row['carbohydrates'],row['proteins'],row['fats']) for index, row in df.iterrows()]
        macro = ['carbohydrates', 'proteins', 'fats', 'kcal']
        df.loc['Total'] = df[macro].sum()
        df.loc['Total'] = df.loc['Total'].fillna('')

        print(df)




