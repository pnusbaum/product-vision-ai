# terraform notatki

To zatrzymuje instancję sql żebym za nią nie płacił.
```
gcloud sql instances patch products-db --activation-policy=NEVER
```
Wznowienie:
```
gcloud sql instances patch products-db --activation-policy=ALWAYS
```
bo place za dzialająca i nieuzywaną instancje


# lokalnie

image-search-api          http://localhost:8000
product-description-api  http://localhost:8081
adminer                  http://localhost:8080
postgres                 localhost:5432
