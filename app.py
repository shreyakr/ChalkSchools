#!/bin/env python

from flask import Flask, request, render_template, flash
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from flask.ext.wtf import Form
from wtforms.validators import DataRequired
from wtforms import IntegerField, TextField, TextAreaField, SubmitField, RadioField

import mysql.connector
import json


app = Flask(__name__)
app.secret_key = 'shreyakumar'

conf = json.load(open ('./sql.conf','r'))

cnx = mysql.connector.connect(user=conf['user'], password=conf['password'],
                              host=conf['host'],
                              database=conf['database'])

model = joblib.load('./height_weight_model/model.pkl')


@app.route('/')
def index():
	form = HeightWeightForm()
	return render_template('landing.html', form=form)

@app.route('/gender')
def get_gender():
	height = request.args.get('height')
	weight = request.args.get('weight')
	pred = model.predict((float(height), float(weight)))
	return pred[0]

@app.route('/predict_gender', methods=['POST'])
def predict_gender():
	form = HeightWeightForm()
	gender_confirm = GenderTruthForm()
	if form.validate() == False:
		flash('All fields are required.')
		return render_template('landing.html', form=form)
	if form.validate_range() == False:
		flash('Fields must be within valid ranges: 50 < height < 80 , 60 < weight< 280')
		return render_template('landing.html', form=form)
	else:
		height = form.height.data
		weight = form.weight.data
		pred = model.predict((float(height), float(weight)))
		gender = pred[0]
		return render_template('gender.html', form=form, gender=gender, gender_form=gender_confirm)

@app.route('/log_result', methods=['POST'])
def log_result():
	form = HeightWeightForm()
	gender_confirm = GenderTruthForm()
	if form.validate() == False:
		flash('All fields are required.')
		return render_template('landing.html', form=form)
	if form.validate_range() == False:
		flash('Fields must be within valid ranges: 50 < height < 80 , 60 < weight< 280')
		return render_template('landing.html', form=form)
	else:
		height = form.height.data
		weight = form.weight.data
		pred = model.predict((float(height), float(weight)))
		gender = pred[0]
		correct = gender_confirm.data['gender_confirm']

		save_response_query = ("INSERT INTO gender_pred_response " \
               + "(height, weight, prediction, is_correct) " \
               + "VALUES (%s, %s, %s, %s, %s)") 

		save_response_data = (height, weight, pred, correct)


		cursor = cnx.cursor()
		cursor.execute(save_response_query, save_response_data)

		return render_template('thanks.html')

 
class HeightWeightForm(Form):
  height = IntegerField("height", validators=[DataRequired()])
  weight = IntegerField("weight", validators=[DataRequired()])
  submit = SubmitField("Send")

  def validate_range(self):
  	# we can only accurately predict for the range of values we have seen in the dataset. Use that for valid range.
  	return (self.height.data > 50 and self.height.data < 80) and (self.weight.data > 60 and self.weight.data < 280)


class GenderTruthForm(Form):
	gender_confirm = RadioField('Am I Right?', choices=[('yes','Correct!'),('no','Incorrect')])



if __name__ == '__main__':
    app.run(debug=True)
