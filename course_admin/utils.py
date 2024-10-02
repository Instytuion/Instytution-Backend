
def restructure_lessons_data(data):
        """Reorganize QueryDict data into a structured lessons list to pass to LessonSerializer"""
        lessons = {}
        
        for key, value in data.lists():
            if key.startswith('lessons'):
                lesson_index = int(key.split('[')[1].split(']')[0])
                
                if lesson_index not in lessons:
                    lessons[lesson_index] = {
                        'lessonName': '',
                        'lessonDescription': '',
                        'week': 0,
                        'images': [],
                        'pdfs': [],
                        'videos': [],
                    }

                if 'pdfs' in key:
                    lessons[lesson_index]['pdfs'].append({'pdf': value[0]})
                elif 'images' in key:
                    lessons[lesson_index]['images'].append({'image': value[0]})
                elif 'videos' in key:
                    lessons[lesson_index]['videos'].append({'video': value[0]})
                else:
                    field_name = key.split(']')[1].lstrip('[').rstrip(']')
                    if field_name == 'week':
                        lessons[lesson_index][field_name] = int(value[0])
                    lessons[lesson_index][field_name] = value[0]

        lessons_list = [lesson_data for lesson_data in lessons.values()]
        return lessons_list

def restructure_update_lesson_data(data):
    lesson_data = {
        'description': '',
        'week': 0,
        'images': [],
        'pdfs': [],
        'videos': [],
    }

    for key, value in data.lists():
        if 'images' in key:
            id = key.split('[')[1].split(']')[0]
            lesson_data['images'].append({'id': id, 'image': value[0]})
        elif 'pdfs' in key:
            id = key.split('[')[1].split(']')[0]
            lesson_data['pdfs'].append({'id': id, 'pdf': value[0]})
        elif 'videos' in key:
            id = key.split('[')[1].split(']')[0]
            lesson_data['videos'].append({'id': id, 'video': value[0]})
        else:
            if key == 'week':
                lesson_data[key] = int(value[0])
            lesson_data[key] = value[0]
    return lesson_data