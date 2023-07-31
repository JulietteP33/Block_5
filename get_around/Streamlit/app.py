import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Config
st.set_page_config(
    page_title="Dashboard",
    page_icon=":car:",
    layout="wide"
)

st.title("Dashboard GetAround")
image_url = "https://lever-client-logos.s3.amazonaws.com/2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943.png"
st.image(image_url, caption=' Getaround image', use_column_width=True)

st.markdown("""
    Welcome to the Getaround dashboard,

    The purpose of this dashboard is to provide an overview of the impact of delays on car rentals. \
    Here we'll identify trends in delays and car re-leasing, and try to find a solution that will increase \
    customer satisfaction while taking into account the interests of the other stakeholders involved. 

""")

st.markdown('---')

# Sidebar markdown
st.sidebar.markdown("## Menu dashboard ")
st.sidebar.markdown("- [Data](#Database)")
st.sidebar.markdown("- [Analysis](#analysis)")
st.sidebar.markdown("- [Conclusion](#conclusion)")

                            ### The csv docs and a few informtion about data
# Data
st.markdown("## Database")

st.subheader('Data Documentation')
@st.cache_data
def load_data():
    data = pd.read_csv('delay_documentation.csv')
    return data

documentation = load_data()

selected_line = st.selectbox("Select a variable :", documentation['field name'])
selected_text = documentation[documentation['field name'] == selected_line]['Comment'].values[0]
with st.expander("See documentation about the variable"):
    st.write(selected_text)


st.subheader('The dataframe')
@st.cache_data
def load_data():
    data = pd.read_csv('data_delay.csv')
    return data

delays = load_data()

st.write(delays)

st.markdown('General information about the data :')

number_exemple = len(delays)
number_connect = delays[delays['checkin_type'] == 'connect'].shape[0]
proportion_connect = (number_connect / number_exemple) * 100
number_cancel = delays[delays['state'] == 'canceled'].shape[0]
proportion_canceled = (number_cancel / number_exemple ) * 100

col1,col2,col3 = st.columns(3)

col1.metric('Number of exemple',int(number_exemple))
col2.metric('% of connected cars',int(proportion_connect))
col3.metric('% of canceled cars',int(proportion_canceled))

st.markdown("The data are highly unbalanced. There is not many cars use connected check-in. \
            And out of 21310 rentals, over 15% have been cancelled.")

st.markdown('---')
                            ###  Cleaning data and analysis for delay

st.markdown("## Analysis")

st.subheader('Delay analysis')

#select state 'ended and cleaning data 
cars = delays[delays['state'] == 'ended']
cars.drop(columns = ['state'], inplace = True)
cars = cars.dropna(subset=['delay_at_checkout_in_minutes'])

# histogram of delay
color = ['#7201a8']

st.markdown('Here is a distribution of the delays among the rentals that took place.')
fig = px.histogram(cars, x='delay_at_checkout_in_minutes', nbins=50,
                   labels={'delay_at_checkout_in_minutes': 'Delay in checkout (minutes)', 'count': 'Quantity'}, color_discrete_sequence=color)

fig.update_layout(title_text='Distribution of delay',
                  xaxis_title_text='Checkout delay (minutes)', yaxis_title_text='Quantity')


st.plotly_chart(fig, use_container_width=True)

st.markdown('There are too many outliers. Some people have returned the car several days early \
            (perhaps someone who has paid but not used the car) \
            and some people have returned the car several days late.')



# Delay category
st.markdown('For ease of interpretation, here is a distribution of the data by category.')
cars['delay_category'] = cars['delay_at_checkout_in_minutes'].apply(lambda x: 'On time or early' if x <= 0
                                                                    else 'less than 15 min' if x <= 15
                                                                    else '1 hour or less of delay' if x <= 60
                                                                    else 'Between 1 and 3 hours of delay' if x <= 180
                                                                    else ' Between 3 and 6 hours of delay' if x <= 360
                                                                    else 'Between 6 hours and one day of delay' if x <= 1440
                                                                    else 'More than one day of delay')
# histogram of delay for each category
color = ['#7201a8']
fig = px.bar(cars['delay_category'].value_counts(),
             x=cars['delay_category'].value_counts().index,
             y=cars['delay_category'].value_counts(),
             labels={'x': 'Category', 'y': 'Quantity'},
             color_discrete_sequence=color)
fig.update_layout(title_text='Delay for each category',
                  xaxis_title_text='Category', yaxis_title_text='Quantity')

st.plotly_chart(fig, use_container_width=True)

# histogram of delay for each category by type of chekin
color = ['#7201a8', '#FBE426']
fig = px.bar(cars, x='delay_category', color='checkin_type',
             color_discrete_sequence=color,
             labels={'delay_category': 'Delay category', 'count': 'Quantity of car'},
             title='Histogram of delay by category for each check-in types')
fig.update_layout(xaxis=dict(tickfont=dict(size=10)),
                  legend=dict(title='Types of check-in', x=1, y=1.0))
st.plotly_chart(fig, use_container_width=True)

                                    ## previous rental analysis
st.markdown('---')
st.subheader('Previous rent')

df_with_previous_rental = cars[cars['previous_ended_rental_id'].notnull()]

# Timedelta category
df_with_previous_rental['time_delta_category'] = df_with_previous_rental['time_delta_with_previous_rental_in_minutes'].apply(lambda x: 'No delay' if x == 0
                                                                    else 'less than 15 min' if x <= 15
                                                                    else '1 hour or less of delta' if x <= 60
                                                                    else 'Between 1 and 3 hours of delta' if x <= 180
                                                                    else ' Between 3 and 6 hours of delta' if x <= 360
                                                                    else 'Between 6 and 12 hours of delta')

# Graph
cars_with_previous_rental = cars[cars['previous_ended_rental_id'] == True].shape[0]
not_previous_rental = cars.shape[0] - cars_with_previous_rental

data = pd.DataFrame({'Status': ['Previously rent', 'Not previously rent'],
                     'Quantity of cars': [cars_with_previous_rental, not_previous_rental]})

# fig 1
color = ['#7201a8', '#FBE426']

cars['Category'] = cars['previous_ended_rental_id'].apply(lambda x: 'previously rent' if pd.notnull(x) else 'not previously rent')
data = cars['Category'].value_counts().reset_index()
data.columns = ['Category', 'Quantity_of_cars']
fig1 = px.bar(data, x='Category', y='Quantity_of_cars', color='Category',
             labels={'Category': 'Category', 'Quantity of cars': 'Number of cars'},
             color_discrete_sequence=color)

fig1.update_layout(title='Number of cars by category',
                  xaxis_title='Category', yaxis_title='Number of cars')

# fig 2
color = ['#FBE426']

fig2 = px.histogram(df_with_previous_rental, x='time_delta_with_previous_rental_in_minutes', nbins=20,
                   color_discrete_sequence=color)
fig2.update_layout(bargap=0.1, title_text='Histogram of timedelta with the previous rental',
                  xaxis_title_text='Time delta with previous rental (in minutes)', yaxis_title_text='Quantity')

# Print them side by side
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1)

with col2:
    st.plotly_chart(fig2)

# by category of timedelta
color = ['#7201a8']

fig = px.bar(df_with_previous_rental['time_delta_category'].value_counts(),
             x=df_with_previous_rental['time_delta_category'].value_counts().index,
             y=df_with_previous_rental['time_delta_category'].value_counts(),
             labels={'x': 'Category', 'y': 'Quantity'},
             color_discrete_sequence=color)

fig.update_layout(title='Timedelta for each category',
                  xaxis_title='Category', yaxis_title='Quantity')

st.plotly_chart(fig, use_container_width=True)

# histogram of delay for each category by type of chekin
cars_previous_rental = len(df_with_previous_rental)
number_of_connect = df_with_previous_rental['checkin_type'].value_counts()['connect']
percent_connect = (number_of_connect / cars_previous_rental ) * 100
st.write(f"Out of {cars_previous_rental} re-rented cars, {number_of_connect} are connected cars. \
         That's around {round(percent_connect, 2)}%.")

color = ['#FBE426', '#7201a8']
fig = px.bar(df_with_previous_rental, x='time_delta_category', color='checkin_type',
             color_discrete_sequence=color,
             labels={'time_delta_category': 'Category', 'count': 'Quantity of car'},
             title='Histogram of delta by category for each check-in types')
fig.update_layout(xaxis=dict(tickfont=dict(size=10)),
                  legend=dict(title='Types of check-in', x=1, y=1.0))
st.plotly_chart(fig, use_container_width=True)


st.markdown('---')
# analysis
# percentage of cars on time
on_time = (cars['delay_category'] == 'On time or early').sum()
total_cars = len(cars)
percentage_on_time = (on_time / total_cars) * 100

# percentage of cars with less than 3 hours delay
fifteen_min = (cars['delay_category'] == 'less than 15 min').sum()
one_hour_or_less = (cars['delay_category'] == '1 hour or less of delay').sum()
less_3_hours = (cars['delay_category'] == 'Between 1 and 3 hours of delay').sum()

less_than_3_hours = fifteen_min + one_hour_or_less + less_3_hours
total_cars = len(cars)
percentage_3_hours = (less_than_3_hours / total_cars) * 100

on_time_and_less_than_3_hours = percentage_on_time + percentage_3_hours

# percentage of cars with less than 3 hours timedelta with the previous rental
no_delay = (df_with_previous_rental['time_delta_category'] == 'No delay').sum()
fifteen_min_timedelta = (df_with_previous_rental['time_delta_category'] == 'less than 15 min').sum()
one_hour_or_less_timedelta = (df_with_previous_rental['time_delta_category'] == '1 hour or less of delta').sum()
less_3_hours_timedelta = (df_with_previous_rental['time_delta_category'] == 'Between 1 and 3 hours of delta').sum()

less_than_3_hours_timedelta = no_delay + fifteen_min_timedelta + one_hour_or_less_timedelta + less_3_hours_timedelta
total_cars_with_previous_rent = len(df_with_previous_rental)
percentage_3_hours_timedelta = (less_than_3_hours_timedelta / total_cars_with_previous_rent) * 100

#sum up
def centered_text(text):
    return f'<div style="text-align:center">{text}</div>'

st.markdown("Sum up for ckeckout:")
st.markdown(centered_text(f"Percentage of cars on time or early: {round(percentage_on_time, 2)}%"),  unsafe_allow_html=True)
st.markdown(centered_text(f" Number of cars with less than 15 min delay: {fifteen_min}"),  unsafe_allow_html=True)
st.markdown(centered_text(f" Number of cars with less than 1 hour delay: {one_hour_or_less}"),  unsafe_allow_html=True)
st.markdown(centered_text(f" Number of cars with less than 3 hours delay: {less_3_hours}"),  unsafe_allow_html=True)
st.markdown(centered_text(f" Percentage of cars with less than 3 hours delay in total: {round(percentage_3_hours, 2)}%"),  unsafe_allow_html=True)
st.markdown(centered_text(f" Cars cheking_out on time and the cars with less than 3 hours delays represent  \
      {round(on_time_and_less_than_3_hours, 2)} % of all cars. We must try to find a solution for \
        the cars with less than 3 hours delays."),  unsafe_allow_html=True)
st.write("")
st.markdown("Sum up for previous rental:")
st.markdown(centered_text(f"On {len(df_with_previous_rental)} cars with previous rental : "),  unsafe_allow_html=True)
st.markdown(centered_text(f"Number of cars with no timedelta: {no_delay}"),  unsafe_allow_html=True)
st.markdown(centered_text(f"Number of cars with less than 15 min timedelta: {fifteen_min_timedelta}"),  unsafe_allow_html=True)
st.markdown(centered_text(f"Number of cars with less than 1 hour timedelta: {one_hour_or_less_timedelta}"),  unsafe_allow_html=True)
st.markdown(centered_text(f"Number of cars with less than 3 hours timedelta: {less_3_hours_timedelta}"),  unsafe_allow_html=True)
st.markdown(centered_text(f"Among the cars rented previously, {round(percentage_3_hours_timedelta, 2)}% were re-rented \
      within three hours. "),  unsafe_allow_html=True)
st.write("")
st.write("")
st.write("")
st.markdown(centered_text("A large number of cars are affected by delays of less than 3 hours and re-let within \
                           the same timeframe. This time gap is problematic. Getaround needs to implement a minimum \
                          delay of 3 hours between rentals in order to ensure a maximum number of rentals on time and \
                           increase customer satisfaction. "),  unsafe_allow_html=True)
st.write("")
st.markdown(centered_text("Very long delays are rare, and with a car rental, several days' delay can mean an \
                          accident, a car in the garage, or an unforeseen event for people far away. These are \
                          parameters we can't do anything about, and it would cost the company more money than it \
                          would bring in, given the number of cars involved. "),  unsafe_allow_html=True)
st.write("")
st.markdown(centered_text("The 3h delay can be applied to both types of car (connected or not). With only 20% of \
                          check-ins for all cars connected, and 43% for re-leased cars, there is no difference in \
                          trends according to the type of check-in."),  unsafe_allow_html=True)
st.write("")
st.markdown(centered_text("From a financial point of view, this will mean a loss of money for rental suppliers, \
                          with 3 hours less rental time between each rotation. In the long term, however, it can\
                           have beneficial effects. If customer satisfaction increases, so will the company's image \
                           and reputation. This could increase the number of annual rentals, make up for the 3 \
                          hours of lost rentals, and perhaps even increase annual revenues."),  unsafe_allow_html=True)
st.write("")

st.markdown('---')

                                ### Conclusion
st.markdown("## Conclusion")
st.markdown("The number of cars re-rented within 12 hours tends to be low. Getaround can afford to set a minimum \
             delta of 3 hours between rentals, to keep the number of customers overlapping on the same rental car \
             to a minimum. Also, as many cars are not re-rented, we could consider always having the models in \
            reserve to be able to make them available if a rental is late for its check-in. To implement this \
            strategy we don't have enough information; we'd need a timeline with the rental durations and dates for \
             each vehicle. ")

st.markdown("In any case, a minimum of 3 hours could increase customer satisfaction. During this non-rental time, \
             there is a loss of money with a lower rental time, but a better brand image also allows for higher \
            prices and greater profitability.")

st.markdown("Another possible strategy for the company would be to look into the reasons behind cancellations\
             - 15% of rentals is a lot, and represents a considerable turnover. There could be a system of deposits \
            levied in the event of cancellation to reduce the loss, or use the trend to overbook like hotels and \
            airplanes. It's a risky practice, and we need more information about the company's figures to be able to \
            establish a strategy. Bear in mind that this is a 'low-cost' business model, and can damage the company's \
            image.")

