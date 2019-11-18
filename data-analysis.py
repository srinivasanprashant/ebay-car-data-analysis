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

# Let's look at the data in the columns date_crawled, ad_created and last_seem
print(autos.loc[:, ["date_crawled", "ad_created", "last_seen"]].head(10))
# Let's further explore the date_crawled column and generate statistics to draw some inferences
print(autos["date_crawled"].str[:10].value_counts(normalize=True, dropna=False))
print(autos["date_crawled"].str[:10].value_counts(normalize=True, dropna=False).sort_index())
# After exploring date_crawled, the data appears to be equally distributed over all days in
# the one-month range, except for the last three days (04-05 to 04-07).
print(autos["ad_created"].str[:10].value_counts(normalize=True, dropna=False))
print(autos["ad_created"].str[:10].value_counts(normalize=True, dropna=False).sort_index())
# The ad created dates range from 2015-06 to 2016-4 (almost 10 months). Most created dates appear
# to be within 1-2 months of the listing date, but a few are almost 10 months old.

print(autos["registration_year"].describe())
# We could clean up this data set by removing values below 1900 or above 2017. The majority of the
# registration date years are between 1999 and 2008. The registration_year column contains some odd values
# The minimum value is 1000, almost a thousand years before cars were invented
# The maximum value is 9999, many years into the future. This is just erroneous data.

# Remove outliers for registration_year, removing rows where
# year is <= 1900 or year > 2017
autos = autos.loc[autos["registration_year"].between(1900, 2017, inclusive=True), :]
print(autos["registration_year"].describe())
print(autos["registration_year"].value_counts(normalize=True, dropna=False))
# The statistics are indicative of the new tighter range of the registration year data

# Use aggregation to understand the brand column
# Explore the unique values in the brand column while limiting ourselves to the top 10
print(autos["brand"].value_counts().head(10))
print(autos["brand"].value_counts(normalize=True).head(10))
print(autos["brand"].value_counts().describe())
# Looking at the top ten list above, the top ten account for almost 25% of all cars listed.
# Thus, the top ten out of 40 would be a good subset of brands to focus on for aggregation analysis.

# Initialize empty dictionaries
brand_mean_price = {}
brand_mean_mileage = {}

# For each of the top ten brands (described above) in our list of data,
# calculate the mean mileage and mean price, and store the results in a dictionary
for brand in autos["brand"].value_counts().head(10).index:
    # assign the mean price to the dictionary, with the brand name as the key
    brand_mean_price[brand] = autos.loc[autos["brand"]==brand,"price"].mean()
    # assign the mean mileage to the dictionary, with the brand name as the key
    brand_mean_mileage[brand] = autos.loc[autos["brand"]==brand,"odometer_km"].mean()
    # print(autos.loc[autos["brand"]==brand,"price"].describe())
# Convert both dictionaries to series objects, using the series constructor
series_brand_mean_price = pd.Series(brand_mean_price)
series_brand_mean_mileage = pd.Series(brand_mean_mileage)
# Create a dataframe from the first series object using the dataframe constructor
df_brand_aggregate = pd.DataFrame(series_brand_mean_price, columns=['mean_price'])
# Assign the other series as a new column in this dataframe
df_brand_aggregate["mean_mileage_km"] = series_brand_mean_mileage
print(df_brand_aggregate.sort_values("mean_mileage_km"))
print(df_brand_aggregate.describe())

# Although Volkswagen is the most popular brand listed, the mean price is not as high as those of Audi,
# BMW or Mercedes-Benz, which are several thousands higher. Fiat, Opel and Renault are at the bottom
# of this list, with mean listed price not even exceeding $3000.

# No clear trend is evident in terms of relationship between mileage and price. The range of average
# mileage listed is very tight, with the more expensive brands showing higher than average mileage.

#TODO
# Data cleaning next steps:
# Identify categorical data that uses german words, translate them and map the values to their english counterparts
# Convert the dates to be uniform numeric data, so "2016-03-21" becomes the integer 20160321.
# See if there are particular keywords in the name column that you can extract as new columns
# Analysis next steps:
# Find the most common brand/model combinations
# Split the odometer_km into groups, use aggregation to see if average prices follows any patterns based on the mileage
# How much cheaper are cars with damage than their non-damaged counterparts?
