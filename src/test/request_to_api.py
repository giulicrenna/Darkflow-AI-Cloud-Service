import requests

consulta: dict = {
  "reportId": "9271678",
  "model": {
    "name": "yolov8x.pt",
    "version": "v1.0.0"
  },
  "enviroment": "DEV",
  "images": [
    {
      "imageId": "000001",
      "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/A-Cat.jpg/2560px-A-Cat.jpg"
    },
    {
      "imageId": "000002",
      "url": "https://upload.wikimedia.org/wikipedia/commons/4/43/Cute_dog.jpg"
    },
    {
      "imageId": "000003",
      "url": "https://st2.depositphotos.com/3591429/5995/i/950/depositphotos_59954731-stock-photo-large-group-of-people.jpg"
    },
    {
      "imageId": "000004",
      "url": "https://images.pexels.com/photos/380769/pexels-photo-380769.jpeg?cs=srgb&dl=pexels-marc-mueller-380769.jpg&fm=jpg"
    }
  ]
}

"""
consulta: dict = {
    'model' : 'darkflow-test.pt',
    'img_arr' : ['https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FDJI_0890.JPG?alt=media&token=cc4809e3-91f4-4734-b883-65ee0b07869e',
                 'https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FDJI_0899.JPG?alt=media&token=ad65ac3e-8fb8-4c8b-9547-8303cd151282',
                 'https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FHirschfeldia_incana.jpg?alt=media&token=97e41b76-4409-4b8b-be69-4e35a248fc2b',
                 'https://firebasestorage.googleapis.com/v0/b/cda-darkflow.appspot.com/o/drone%2FDJI_0903.JPG?alt=media&token=a6dd1aa0-4168-4198-b91c-852d057af550']
}
"""

rta = requests.post('http://200.45.208.5:8000/multiple_detection', json=consulta)

print(rta.text)