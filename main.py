from argparse import *
from models import *
from datetime import datetime
import re

class Menu(ArgumentParser):
    def __init__(self, database_operator):
        super().__init__()
        self.database_operator=database_operator
        self.__create_and_set_options()

    def __create_and_set_options(self):
        '''
        Creating options of menu and setting the proper configuration.
        '''
        subparsers = self.add_subparsers(parser_class=ArgumentParser)

        parser_add_a_meal = subparsers.add_parser('add-a-meal') #name, ean, c,f,p, weight, date
        parser_add_a_meal.add_argument('--name', type=str, default='meal')
        parser_add_a_meal.add_argument('--ean', type=str, default='N'+re.sub(r"[^0-9]","",str(datetime.now()))[2:])
        parser_add_a_meal.add_argument('-c','--carbohydrates', type=float)
        parser_add_a_meal.add_argument('-p','--proteins', type=float)
        parser_add_a_meal.add_argument('-f','--fats', type=float)
        parser_add_a_meal.add_argument('-w','--weight',type=float, default=100)
        parser_add_a_meal.add_argument('-d','--date', type=str, default=str(date.today()))
        parser_add_a_meal.set_defaults(function=self.database_operator.add_a_meal)

        parser_save_a_meal_in_the_database = subparsers.add_parser('save-a-meal-in-the-database') #name, ean, c,f,p, weight
        parser_save_a_meal_in_the_database.add_argument('name', type=str)
        parser_save_a_meal_in_the_database.add_argument('ean', type=str)
        parser_save_a_meal_in_the_database.add_argument('carbohydrates', type=float)
        parser_save_a_meal_in_the_database.add_argument('proteins', type=float)
        parser_save_a_meal_in_the_database.add_argument('fats', type=float)
        parser_save_a_meal_in_the_database.add_argument('-w','--weight',type=float, default=100)
        parser_save_a_meal_in_the_database.set_defaults(function=self.database_operator.save_a_meal_in_the_database)

        parser_show_today = subparsers.add_parser('show-today')
        parser_show_today.add_argument('--foos', type=int)
        parser_show_today.set_defaults(function=self.database_operator.temp)

        parser_show_stats = subparsers.add_parser('show-stats') #startdate, enddate
        parser_show_stats.add_argument('foods', type=int)



database_operator = DatabaseOperator(db, 'database.db')
menu = Menu(database_operator)
args=menu.parse_args()
try:
    args.function(args)
except CCAppException as e:
    print('CalorieCounterApp error: {}'.format(e) )
except Exception as e:
    print('General error:  {}'.format(e))
