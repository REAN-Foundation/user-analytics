
# User Analytics Report

## Table of Contents

- [User Analytics Report](#user-analytics-report)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Basic Statistics](#basic-statistics)
    - [Overview](#overview)
    - [Demographics](#demographics)
  - [Generic Engagement Metrics](#generic-engagement-metrics)
    - [Daily, Weekly, and Monthly Active Users](#daily-weekly-and-monthly-active-users)
    - [Retention Rates on specific days](#retention-rates-on-specific-days)
    - [Retention Rates during specific intervals](#retention-rates-during-specific-intervals)
    - [Login Frequency](#login-frequency)
    - [Average Session Duration](#average-session-duration)
    - [Most Commonly Visited Screens](#most-commonly-visited-screens)
    - [Most Commonly Used Features](#most-commonly-used-features)
  - [Feature Engagement Metrics](#feature-engagement-metrics)
    - [Feautre Engagement Metrics Definitions](#feautre-engagement-metrics-definitions)
      - [Feature Access Frequency](#feature-access-frequency)
      - [Average Usage Duration](#average-usage-duration)
      - [Feature Engagement Rate](#feature-engagement-rate)
      - [Feature Retention Rate on specific days](#feature-retention-rate-on-specific-days)
      - [Feature Retention during specific intervals](#feature-retention-during-specific-intervals)
      - [Feature Drop-Off Points](#feature-drop-off-points)
      {{feature_engagement_table_content}}   
    - [Appendix A :](#appendix-a-)
        - [Registration and Deregistration History Table](#registration-and-deregistration-history-table)

---

## Introduction

This report provides an analysis of general usage statistics, system-wide and feature-wise user engagement metrics.

The analysis is performed considering the following contraints.

{{report_details_table}}

---

## Basic Statistics

This section provides an overview of the basic analytics related to the tenant, including the total number of users, patient statistics, and registration/deregistration history.

### Overview

{{basic_statistics_overview_table}}

**Registration / Deregistration History**
Trends of how many users registered or deregistered from the system on a given day, in a given week or a month.

**Registration and Deregistration History**

{{registration_history_chart}}

{{deregistration_history_chart}}

---

### Demographics

Demographics provide an understanding of the user base by categorizing them into age, gender, location, and other key attributes. These groupings help identify user diversity and engagement patterns.

**Age Distribution**

{{age_distribution_chart}}

{{age_distribution_table}}

**Gender Distribution**

{{gender_distribution_chart}}

{{gender_distribution_table}}

**Ethnicity Distribution**

{{ethnicity_distribution_chart}}

{{ethnicity_distribution_table}}

**Race Distribution**

{{race_distribution_chart}}

{{race_distribution_table}}

**Health System Distribution**

{{health_system_distribution_chart}}

{{health_system_distribution_table}}

**Hospital Affiliation Distribution**

{{hospital_affiliation_distribution_chart}}

{{hospital_affiliation_distribution_table}}

**Caregiver or Stroke Survivor Distribution**

{{caregiver_or_stroke_survivor_distribution_chart}}

{{caregiver_or_stroke_survivor_distribution_table}}

---

## Generic Engagement Metrics

This section captures key metrics that provide insight into how users interact with the system, including daily activity, session duration, and retention.

### Daily, Weekly, and Monthly Active Users

- **Daily Active Users (DAU)**: Total number of unique users who interact with the platform on a given day.

\[
DAU(t) = \sum_{i=1}^{n} \text{Active Users on Day } t
\]

{{daily_active_users_chart}}

- **Weekly Active Users (WAU)**: Total number of unique users who interact with the platform during a week.

\[
WAU(t) = \sum_{i=1}^{n} \text{Active Users in Week } t
\]

{{weekly_active_users_chart}}

- **Monthly Active Users (MAU)**: Total number of unique users who interact with the platform during a month.

\[
MAU(t) = \sum_{i=1}^{n} \text{Active Users in Month } t
\]

{{monthly_active_users_chart}}

---

### Retention Rates on specific days

  The percentage of users who return to the app after their first use at specific intervals (day 1, day 7, day 30). Retention rates measure user loyalty and the ability of the platform to keep users engaged over time.

\[
\text{Retention Rate on Day } n = \frac{\text{Number of Users on Day } n}{\text{Number of Users on Day 0}} \times 100
\]

{{retention_rate_On_specific_days_chart}}

{{retention_rate_On_specific_days_table}}

Retention rates help identify how well the platform retains users over time, indicating the effectiveness of engagement strategies and feature enhancements. Retention rates measure user loyalty and the ability of the platform to keep users engaged over time.


### Retention Rates during specific intervals

  The percentage of users who return to the app after their first use at specific intervals (0-1 days, 1-3 days, 3-7 days, etc). This is just another way to look at the retention on specific days.

\[
\text{Retention Rate during interval } = \frac{\text{Number of Users returning during interval } }{\text{Number of Users on Day 0}} \times 100
\]

{{retention_rate_in_specific_intervals_chart}}

{{retention_rate_in_specific_intervals_table}}

---

### Login Frequency

  Average number of times users log into the system per day, week, or month.

\[
\text{Login Frequency (monthly)} = \frac{\text{Total Logins in a Month}}{\text{Number of Active Users in that Month}}
\]

This metric shows how often users are logging into the platform, which is an indicator of how integral the platform is to users' daily lives.

{{login_frequency_monthly_chart}}

{{login_frequency_monthly_table}}

### Average Session Duration

  ___Average Session length = {{average_session_length}} Minutes___

  The average session length in minutes the users have spent on the app/platform.
  This is measured as the duration of a session based on the difference between the first and last event timestamps in that session. In many cases, especially previously synched data, this session information is not available and we can use the average time spent on the platform between first and last event captured for the user.
  This may not be the most accurate representation of the session duration but it gives a good idea of how long users are spending on the platform.

### Most Commonly Visited Screens

  The most frequently visited screens or features within the platform, indicating where the user spent most of their time.

  {{most_commonly_visited_screens_table}}
  

### Most Commonly Used Features

  The most frequently used features within the platform, indicating user preferences and popular functionalities.

  {{most_commonly_used_features_table}}

---

## Feature Engagement Metrics

This section focuses on how users interact with specific features, including access frequency, usage duration, and drop-off points.

### Feautre Engagement Metrics Definitions

#### Feature Access Frequency

The number of times users access a particular feature over time. This metric helps identify the popularity and utility of features among users.

\[
\text{Feature Access Frequency (Monthly)} = \frac{\text{Total Feature Accesses in a Month}}{\text{Number of Active Users in a Month}}
\]

#### Average Usage Duration

The average amount of time users spend on a particular feature during each session. This metric shows how much time users invest in interacting with a specific feature, indicating the depth of engagement.

\[
\text{Average Usage Duration (minutes)} = \frac{\text{Total Time Spent on Feature}}{\text{Total Feature Sessions}}
\]

#### Feature Engagement Rate

This is the ratio of number of unique users engaging with each feature per month to the total number of active users per month.

\[
\text{Feature Engagement Rate} = \frac{\text{Number of Unique Users Engaging with Feature}}{\text{Total Active Users in Month}}
\]

#### Feature Retention Rate on specific days

The percentage of users who return to a feature after their first use at specific intervals (day 1, day 7, day 30). Retention rates measure user loyalty and the ability of the feature to keep users engaged over time.

\[
\text{Feature Retention Rate on Day } n = \frac{\text{Number of Users on Day } n}{\text{Number of Users on Day 0}} \times 100
\]

#### Feature Retention during specific intervals

The percentage of users who return to a feature after their first use at specific intervals (0-1 days, 1-3 days, 3-7 days, etc). This is just another way to look at the retention on specific days.

\[
\text{Feature Retention Rate during interval } = \frac{\text{Number of Users returning during interval } }{\text{Number of Users on Day 0}} \times 100
\]

#### Feature Drop-Off Points

Points in the user flow where users most frequently stop using a feature. Identifying drop-off points helps in optimizing the user journey and addressing usability challenges to improve feature completion rates.
These are found by identifying the most common sequences of events that lead to users dropping off from a feature.

| Sequence | Drop-Off Point        | Count | Percentage |
|----------|-----------------------|-------|------------|
| 1        | Feature A -> Feature B -> Feature C -> Feature D | 2000  | 40%        |
| 2        | Feature A -> Feature B -> Feature C | 1500  | 30%        |
| 3        | Feature A -> Feature B | 1000  | 20%        |
| 4        | Feature A | 500   | 10%        |

{{all_features_data}}

### Appendix A :

##### Registration and Deregistration History Table

{{registration_deregistration_table}}


