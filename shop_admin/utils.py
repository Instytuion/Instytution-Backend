def restructure_product_creation_data(data):
    print("request data ", data)
    product_data = {
        'name': '',
        'sub_category': '',
        'description': '',
        'is_active': True,
        'images': [],
        'details': []
    }

    for key, value in data.lists():
        if 'sub_category[name]' in key:
            product_data['sub_category'] = {'name': value[0]}
        elif key == 'name':
            product_data['name'] = value[0]
        elif key == 'description':
            product_data['description'] = value[0]
        elif key.startswith('images'):
            # Parsing the image index and attribute (either 'image' or 'color')
            image_index = int(key.split('[')[1].split(']')[0])
            image_field = key.split('][')[1].strip(']')

            # Ensure the list is large enough to hold the current index
            while len(product_data['images']) <= image_index:
                product_data['images'].append({'image': "", 'color': ""})
            
            # Update the correct attribute for this image entry
            product_data['images'][image_index][image_field] = value[0]
        elif key.startswith('details'):
            # Parsing the detail index and attribute (color, price, stock, size)
            detail_index = int(key.split('[')[1].split(']')[0])
            detail_field = key.split('][')[1].strip(']')

            # Ensure the list is large enough to hold the current index
            while len(product_data['details']) <= detail_index:
                product_data['details'].append({'color': '', 'price': 0, 'stock': 0, 'size': ''})

            # Update the correct attribute for this detail entry
            if detail_field == 'color':
                product_data['details'][detail_index]['color'] = value[0]
            elif detail_field == 'price':
                product_data['details'][detail_index]['price'] = float(value[0])
            elif detail_field == 'stock':
                product_data['details'][detail_index]['stock'] = int(value[0])
            elif detail_field == 'size':
                product_data['details'][detail_index]['size'] = value[0]

    return product_data
