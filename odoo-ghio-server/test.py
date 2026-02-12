
payload = {
    'nombre': 'Nuevo Cliente',
    'email': 'jose.cruzal@outlook.com',
    'Ciudad': 'San Salvador',
    'telefono': '78787878',
    'seleccion': ['Producto A', 'Producto B'],
}

write_vals = {}
# fields_required = ['nombre', 'email', 'Ciudad', 'telefono', 'seleccion']
fields_required = {
    'nombre': ['contact_name', 'name'],
    'email': ['email_from'],
    'Ciudad': ['city'],
    'telefono': ['phone', 'mobile'],
    'seleccion': ['description'],
}

if payload:
    write_vals["description"] = str(payload)

for field, odoo_fields in fields_required.items():
    value = payload.get(field) or None
    if value:
        if field == 'seleccion' and type(value) is list:
            value = ', '.join(value)
        for odoo_field in odoo_fields:
            write_vals[odoo_field] = value


print(str(write_vals))

# Escribimos si hay cambios que aplicar
if write_vals:
    # El lead esta en la variable 'record'
    record.sudo().write(write_vals)

# print(str(payload)) # Podemos usar el ir.logging para guardar los logs