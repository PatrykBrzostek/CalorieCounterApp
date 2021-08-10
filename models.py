from calories_calculator import Calculator
from peewee import *
from datetime import date, datetime, timedelta
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
                if all(i is None for i in macro):
                    raise CCAppValueErrorException('The EAN number {} is not in the database. At least one of the macronutrients has to have defined value.'.format(args.ean))
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
        today=str(date.today()-timedelta(days=5))
        if Day.filter(Day.date==today):
            query = Day.select(Meal.name, Meal.ean, Day.weight, Meal.carbohydrates, Meal.proteins, Meal.fats).join(Meal).where(Day.date == today)
            df = pd.DataFrame(list(query.dicts()))
            df['kcal']=[self.calculator.get_portions_scale(row['weight'])*self.calculator.count_calories(row['carbohydrates'],row['proteins'],row['fats']) for index, row in df.iterrows()]
            columns= ['carbohydrates', 'proteins', 'fats', 'kcal']
            df.loc['Total'] = df[columns].sum()
            df.loc['Total'] = df.loc['Total'].fillna('')
            print(df)
        else:
            raise CCAppNoDataException("No meals added today. Use 'add-a-meal -h' to show how add a meal.")

    def show_stats(self, args):
        try:
            datetime.strptime(args.start_date, '%Y-%m-%d')
            datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            raise CCAppDataFormatException("Incorrect data format, should be YYYY-MM-DD")

        if args.start_date>args.end_date:
            raise CCAppValueErrorException('Incorrect data value. Start date should be earlier than end date.')
        elif args.start_date>str(date.today()) or args.end_date>str(date.today()):
            raise CCAppValueErrorException('Incorrect data value. Start and end dates should be earlier than today date.')
        else:
            query = Day.select(Day.date, Day.weight, Meal.carbohydrates, Meal.proteins, Meal.fats).join(
                Meal).where(Day.date <=args.end_date and Day.date >= args.start_date)
            df = pd.DataFrame(list(query.dicts()))
            df['kcal'] = [self.calculator.get_portions_scale(row['weight'])*self.calculator.count_calories(row['carbohydrates'], row['proteins'], row['fats']) for index, row
                          in df.iterrows()]
            columns = ['carbohydrates', 'proteins', 'fats', 'kcal']
            df_grouped_by_date = df.groupby('date', as_index=False)[columns].sum()
            print(df_grouped_by_date.to_string(index=False))



