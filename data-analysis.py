# The aim of this project is to clean the data and analyze the included used car listings
# The data dictionary provided with data is as follows:
#
# dateCrawled - When this ad was first crawled. All field-values are taken from this date.
# name - Name of the car.
# seller - Whether the seller is private or a dealer.
# offerType - The type of listing
# price - The price on the ad to sell the car.
# abtest - Whether the listing is included in an A/B test.
# vehicleType - The vehicle Type.
# yearOfRegistration - The year in which the car was first registered.
# gearbox - The transmission type.
# powerPS - The power of the car in PS.
# model - The car model name.
# kilometer - How many kilometers the car has driven.
# monthOfRegistration - The month in which the car was first registered.
# fuelType - What type of fuel the car uses.
# brand - The brand of the car.
# notRepairedDamage - If the car has a damage which is not yet repaired.
# dateCreated - The date on which the eBay listing was created.
# nrOfPictures - The number of pictures in the ad.
# postalCode - The postal code for the location of the vehicle.
# lastSeenOnline - When the crawler saw this ad last online.

import pandas as pd
import re
pd.set_option('display.max_columns', 500)
pd.options.display.width = 0
pd.options.display.float_format = '{:.3f}'.format


# Function to convert camel case to snake case
def convert_to_snakecase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# reading csv file
autos = pd.read_csv("autos.csv", encoding='latin1')

# Change the columns from camelcase to snake-case.
# Change a few wordings to more accurately describe the columns.

autos_header = []
for column_name in autos.columns:
    if column_name == "yearOfRegistration":
        column_name = "registration_year"
    elif column_name == "monthOfRegistration":
        column_name = "registration_month"
    elif column_name == "notRepairedDamage":
        column_name = "unrepaired_damage"
    elif column_name == "dateCreated":
        column_name = "ad_created"
    elif column_name == "abtest":
        column_name = "ab_test"
    elif column_name == "nrOfPictures":
        column_name = "num_photos"
    else:
        column_name = convert_to_snakecase(column_name)
    autos_header.append(column_name)

autos.columns = autos_header

# print(autos.head())
# print(autos.tail())
# autos.info()

# Perform basic data exploration to determine what other cleaning tasks need to be done
# Use DataFrame.describe() to look at descriptive statistics for all columns
print(autos.describe(include='all'))

# Columns that can be good candidates to drop from analysis are seller, offer_type, and num_photos
print(autos["seller"].value_counts())
print(autos["offer_type"].value_counts())
print(autos["num_photos"].value_counts())

# drop the columns identified above
autos.drop(["seller", "offer_type", "num_photos"], axis=1)
# rename column kilometer to "odometer_km" to be more representative
autos.rename({"kilometer": "odometer_km"}, axis=1, inplace=True)


# Continue exploring the data, specifically looking for data that doesn't look right
# Analyze the columns using minimum and maximum values and look for any values that
# look unrealistically high or low (outliers) that we might want to remove.

print(autos["odometer_km"].unique().shape)
print(autos["odometer_km"].describe())
print(autos["odometer_km"].value_counts().sort_index(ascending=False))

# Looking at the details and frequency table of values for odometer_km, there are clearly preset mileage
# levels that the cars have been put into with the intervals varying (not equally distributed). Also, there
# are a lot more high-mileage cars in the data-set, which can be expected. There doesn't seem to be anything
# wrong with this data, so let's keep it and look at price.

pd.options.display.float_format = '{:.2f}'.format
print(autos["price"].unique().shape)
print(autos["price"].describe())
print(autos["price"].value_counts().head(10))
print(autos["price"].value_counts().sort_index(ascending=False).head(10))

# Remove outliers for price, removing rows where price is zero or > 500,000
autos = autos.loc[autos["price"].between(0, 500000, inclusive=False), :]
print(autos["price"].unique().shape)
print(autos["price"].describe())
print(autos["price"].value_counts().head(10))
# print(autos.head())
