import numpy as np
from flask import Flask, jsonify, render_template

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

'''DB Setup'''

engine = create_engine('sqlite:///Resources/belly_button_biodiversity.sqlite')

#reflect the db into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

#make references to the tables
otu = Base.classes.otu
samp = Base.classes.samples
metadata = Base.classes.samples_metadata

#create a session
session = Session(engine)

#make an app instance
app = Flask(__name__)

'''Define the Routes'''

#index
@app.route('/')
def index():
    return render_template('index.html')

#sample names
@app.route('/names')
def names():
    '''returns a list of the sample names'''
    
    #initialize list
    names_list = []
    
    #append 'BB_' to all the ids in the metadata table
    for sample_id in session.query(metadata.SAMPLEID).all():
        names_list.append(f"BB_{sample_id[0]}")

    return jsonify(names_list)

#otu descriptions
@app.route('/otu')
def otu_descs():
    '''returns a list of OTU descriptions'''
    
    #otu descriptions
    otu_desc_list = session.query(otu.lowest_taxonomic_unit_found).all()

    #make the list of tuples a normal list
    otu_desc_list = list(np.ravel(otu_desc_list))

    return jsonify(otu_desc_list)

#sample metadata
@app.route('/metadata/<sample>')
def samp_md(sample=None):
    '''returns a json dictionary of sample metadata'''

    #make a list with the needed keys
    key_names = ['AGE', 'BBTYPE', 'ETHNICITY', 'GENDER', 'LOCATION', 'SAMPLEID']

    #remove the 'BB_' from sample 
    sample_id = sample.strip('BB_')

    #find the metadata for the given sample
    sample_metadata = session.query(metadata).filter_by(SAMPLEID = sample_id).scalar()

    #initialize the dictionary
    metadata_dict = {}

    #add the keys,values to the dict
    for name in key_names:
        #use getattr(object, name) to get sample_metdata.name
        metadata_dict[name] = getattr(sample_metadata, name)

    #return jsonified dictionary
    return jsonify(metadata_dict)

#weekly washing frequency
@app.route('/wfreq/<sample>')
def wash_freq(sample=None):
    '''returns an integer for the weekly washing frequency'''

    #remove the 'BB_' from sample 
    sample_id = sample.strip('BB_')

    #find the washing frequency
    wfreq = session.query(metadata.WFREQ).filter_by(SAMPLEID = sample_id).scalar()
    
    return wfreq

#otu ids and sample values
@app.route('/samples/<sample>')
def otu_sample(sample=None):
    '''
    returns a list of a dictionary containing sorted lists for otu_ids and sample_values
    '''

    #get the two columns and sort descending by sample values
    results = session.query(samp.otu_id, getattr(samp, sample)).\
        order_by(getattr(samp, sample).desc()).all()

    #unpack the tuples
    otu_ids, samples = zip(*results)

    #make them into lists
    otu_list = list(otu_ids)
    sample_list = list(samples)

    #make the dictionary
    otu_sample_dict = {'otu_ids': otu_list, 'sample_values': sample_list}

    #make a list of the dictionary
    dict_list = [otu_sample_dict]

    return jsonify(dict_list)

#run the app
if __name__ == '__main__':
    app.run(debug=True)