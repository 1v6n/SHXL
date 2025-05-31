import random


def before_scenario(context, scenario):
    random.seed(42)


# This file is now moved to features/support/environment.py
