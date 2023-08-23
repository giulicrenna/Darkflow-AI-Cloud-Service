import requests

consulta: dict = {
    'model' : 'darkflow-test.pt',
    'img_arr' : ['https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FDJI_0890.JPG?alt=media&token=cc4809e3-91f4-4734-b883-65ee0b07869e',
                 'https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FDJI_0899.JPG?alt=media&token=ad65ac3e-8fb8-4c8b-9547-8303cd151282',
                 'https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FHirschfeldia_incana.jpg?alt=media&token=97e41b76-4409-4b8b-be69-4e35a248fc2b',
                 'https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FDJI_0903.JPG?alt=media&token=a6dd1aa0-4168-4198-b91c-852d057af550']
}

rta = requests.post('http://190.2.104.63:8000/simple_detection', json=consulta)

print(rta.text)