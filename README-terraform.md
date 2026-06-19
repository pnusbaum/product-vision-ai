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


