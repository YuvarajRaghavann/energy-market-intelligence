# Interview guide

## Project fundamentals

1. Why did you choose this dataset?
2. What are the main tables in your data model?
3. What does a row represent?
4. Which indicators did you choose and why?
5. What are the units of the key indicators?
6. How do you refresh the dataset?
7. How do you make the pipeline reproducible?

## Data quality

1. How did you detect duplicates?
2. How did you handle missing values?
3. Why did you flag outliers instead of automatically removing them?
4. How would you investigate a sudden jump in production?
5. How would you detect a schema change in the source?
6. How would you validate a new source before merging it?

## SQL / databases

1. Why use PostgreSQL?
2. What is the grain of `fact_energy_annual`?
3. Why is `(country, year)` the primary key?
4. Which indexes help common analyst queries?
5. How would you optimize a slow country-year query?
6. How would you design the schema for multiple source versions?

## Statistics / forecasting

1. Why use a naive baseline?
2. Why use time-series cross-validation rather than random train/test splitting?
3. What do MAE and RMSE tell you?
4. Why might a random forest overfit a small annual dataset?
5. What would you do with more observations?
6. Which external variables could improve the model?
7. Why should the forecast not be described as a commodity-price prediction?

## Research thinking

1. What business question does the dashboard answer?
2. How would you turn a dataset into a client-facing insight?
3. What would you verify before publishing a surprising result?
4. How would you communicate uncertainty?
5. How would you compare two countries fairly when their populations are very different?

## Rystad-specific positioning

Do not claim experience you do not have.

A defensible framing is:

> "I built a public-data energy analytics project specifically to practice the end-to-end workflow of collecting, validating, modeling and communicating energy data. It is not based on Rystad proprietary datasets."

That keeps the project credible while demonstrating the relevant technical workflow.
