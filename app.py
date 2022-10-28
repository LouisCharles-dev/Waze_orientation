from cProfile import label
from flask import Flask, render_template, request
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from fonction import handle_rome, scrapper_formation, handle_modalite, handle_parcours
import os

app = Flask(__name__)

#-----------------------------------------Préparation model et dataset---------------------------------------------------------
dfX1 = pd.read_json('df_cluster_rome1.json')
dfX2 = pd.read_json('df_cluster_rome2.json')

df_cluster_rome = pd.concat([dfX1, dfX2], ignore_index=True, sort=False)
model =  SentenceTransformer("dangvantuan/sentence-camembert-large")

#-----------------------------------------------Page d'acceuil-----------------------------------------------------------------

@app.route('/', methods=['POST', 'GET'])
def table():

    return render_template('table.html')


#-----------------------------------------------Page détails métiers-------------------------------------------------------------

@app.route('/detail_metier', methods=['POST', 'GET'])

def detail_metier():

  label = request.args['label']
  data = df_cluster_rome
  data = data[['code_ROME','Libellé ROME']]
  data = data[['code_ROME','Libellé ROME']]
  data = data[data['Libellé ROME']==label]
  rome_value = data['code_ROME'].iloc[0]
  df_detail_metier = pd.read_csv('textes-rome-compact.csv')
  df_detail_metier = df_detail_metier[df_detail_metier['ROME_PROFESSION_CARD_CODE']==rome_value]

  return render_template('metiers_detail.html', recherche_text=df_detail_metier.TXT_NAME.tolist())


#-----------------------------------------------Page recherche-----------------------------------------------------------------

@app.route('/handle_data', methods=['POST'])

def handle_data():

  projectpath = request.form['camenBERT']
  requete_code = model.encode(projectpath)
  laliste = []

  for i in list(df_cluster_rome['encoding_label']):
    laliste.append(i) 

  score_cos = cosine_similarity([requete_code],laliste)
  score_cos = score_cos.tolist()

  d = {'sentence': df_cluster_rome['Libellé ROME'], 'score': score_cos[0]}
  df = pd.DataFrame(data=d)
  df = df.sort_values(by=['score'], ascending=False)

  return render_template('recherche.html', recherche_text=df.sentence.iloc[0:4].tolist())
  
  

#-----------------------------------------------Page formations----------------------------------------------------------------

@app.route('/search_rome', methods=['GET'])
def search_rome():

  label = request.args['label']
  data = df_cluster_rome
  data = data[['code_ROME','Libellé ROME']]
  data = data[data['Libellé ROME']==label]
  return render_template('formation.html', rome_text=handle_rome(data['code_ROME'].iloc[0]), rome_value = data['code_ROME'].iloc[0])

  
#-----------------------------------------------Page formations modalité----------------------------------------------------------------

@app.route('/search_modalite', methods=['GET'])
def search_modalite():

    moda = request.args['mod']
    rom = request.args['rom']
    try : 
      certifiante = request.args['certifiante']
      certifiante = 'certifiante=true'
      return render_template('formation_filtre.html', rome_text=handle_modalite(rom, moda, certifiante), rome = rom)
    except :
            try :
              alternance = request.args['alternance']
              alternance = 'alternance=true'
              print(alternance)
              return render_template('formation_filtre.html', rome_text=handle_modalite(rom, moda, alternance), rome = rom)
            except :
              try :
                niveauDeSortie = request.args['niveauDeSortie']
                niveauDeSortie = 'niveauDeSortie='+ niveauDeSortie
                print(niveauDeSortie)
                return render_template('formation_filtre.html', rome_text=handle_modalite(rom, moda, 0, 0, niveauDeSortie), rome = rom)
              except:
                return render_template('formation_filtre.html', rome_text=handle_modalite(rom, moda), rome = rom)

#-----------------------------------------------Page parcours----------------------------------------------------------------

@app.route('/search_parcours', methods=['GET'])
def search_parcours():

  rom = request.args['rom']

  return render_template('parcours.html', rome_text=handle_parcours(rom), rome_value = rom)

#-----------------------------------------------Page detail sur formation------------------------------------------------------

@app.route('/search_formation', methods=['GET'])
def search_formation():

  formation = request.args['formation']

  return render_template('formation_detail.html', formation_text=scrapper_formation(formation))

if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
