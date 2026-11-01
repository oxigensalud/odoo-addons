Customizations to PGCE for Oxigen

## Impuestos legacy

Mantenemos algunos impuestos de v11 que eran usados como hijos, se mantienen para
poder usar el tax template en el 303 y poder cubrir un periodo de transición
en el que hay datos generados en v11 (usando tax de tipo grupo) y en v14 (solo
se usa el antiguo padre, ya sin hijos, y con repartition lines).

Las repartition lines son obligatorias en v14 y se añaden consecuentemente
para poder hacer el chart update.

Las `tag_ids` de las repartition lines pueden tener o no tener las casillas del 303,
en cualquier caso si algún día se quieren usar, deberán ser revisadas.

Estos impuestos se encuentran en el CSV `data/account.tax-es_common_mainland.csv (119-269)`.
