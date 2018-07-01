import threading
import urwid

from .. import KEYS
from .. import CHROMATIC_SHARP
from .. import CHROMATIC_FLAT

from ..questionbase import QUESTION_CLASSES

KEY_PADS = {
    'C#': 1,
    'Db': 1,
    'D#': 0,
    'Eb': 0,
    'F#': 1,
    'Gb': 1,
    'G#': 0,
    'Ab': 0,
    'A#': 0,
    'Bb': 0
}

SPACE_CHAR = ' '

def is_chromatic(key):
    if len(key) == 2:
        return True
    return False

class KeyboardButton(urwid.Padding):
    def __init__(self, top="", middle="", bottom="", *args, **kwargs):
        self.text = [urwid.Text(str(item)) for item in [top, middle, bottom]]
        self.lines = urwid.Pile(self.text)
        self.fill = urwid.Filler(self.lines)
        self.adapter = urwid.BoxAdapter(self.fill, height=3)
        self.pad = urwid.Padding(self.adapter)
        self.attr = urwid.AttrMap(w=self.pad, attr_map='default')
        self.box = urwid.LineBox(self.attr)
        # self.attr = urwid.AttrMap(w=self.box, attr_map='default')
        
        super(KeyboardButton, self).__init__(w=self.box, *args, **kwargs)
        
    def highlight(self, state=False):
        #print('were in highlight: ', state)
        if not state:
            #self.attr.set_attr_map({'highlight': 'default'})
            #self.attr.render(('pack', None))
            #self.attr.render((3,))
            #self.original_widget.set_attr_map({'highlight': 'default'})
            #self.original_widget = urwid.AttrMap(w=self.pad, attr_map='default')
            #self.attr = urwid.AttrMap(w=self.box, attr_map='default')
            self.attr = urwid.AttrMap(w=self.pad, attr_map='default')
            self.box = urwid.LineBox(self.attr)
            #self.original_widget = urwid.LineBox(self.attr)
            #self.original_widget = self.box
            #self.original_widget = urwid.LineBox(self.attr)
            self.original_widget = self.box
        else:
            #self.attr.set_attr_map({'default': 'highlight'})
            #self.attr.render(size=('pack', None))
            #self.attr.render((3,))
            #self.original_widget.set_attr_map({'highlight': 'default'})
            #self.original_widget = urwid.AttrMap(w=self.pad, attr_map='highlight')
            self.attr = urwid.AttrMap(w=self.pad, attr_map='highlight')
            self.box = urwid.LineBox(self.attr)
            
            self.original_widget = self.box
        
class Keyboard(urwid.Filler):
    def __init__(self, tonic, show_octave=True, *args, **kwargs):
        
        self.key_index = {}
        
        
        if tonic in KEYS:
            scale = CHROMATIC_SHARP if tonic in CHROMATIC_SHARP else CHROMATIC_FLAT
            idx = scale.index(tonic)
            key_scale = scale[idx:] + scale[:idx]
            
        chromatic_keys = list()
        diatonic_keys = list()

        is_key_chromatic = is_chromatic(tonic)
        
        if is_key_chromatic:
            diatonic_keys.append(('weight', 0.5, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
        else:
            chromatic_keys.append(('weight', 0.5, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
        
        first_chromatic = [note for note in key_scale if len(note) == 2][0]
        # last_chromatic = [note for note in key_scale if len(note) == 2][-1]
        
        for idx, note in enumerate(key_scale):
            
            if is_chromatic(note):
                
                if KEY_PADS[note] == 1 and note != first_chromatic:
                    chromatic_keys.append(('weight', 1, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
                    
                chromatic_keys.append(('weight', 1, KeyboardButton(note)))
                self.key_index.update({note: chromatic_keys[-1]})
            else:
                diatonic_keys.append(KeyboardButton(note))
                self.key_index.update({note: diatonic_keys[-1]})
                
        if show_octave:
            if is_chromatic(tonic):
                if KEY_PADS[tonic] == 1:
                    chromatic_keys.append(('weight', 1, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
                chromatic_keys.append(('weight', 1, KeyboardButton(tonic)))
                self.key_index.update({note: chromatic_keys[-1]})
            else:
                diatonic_keys.append(KeyboardButton(tonic))
                self.key_index.update({note: diatonic_keys[-1]})
                
        if is_key_chromatic:
            if not show_octave:
                weight = 0.5 + KEY_PADS[first_chromatic] + (int(show_octave)/2)
                chromatic_keys.append(('weight', weight, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
            else:
                weight = 0.5 #+ KEY_PADS[first_chromatic] + (int(show_octave)/2)
                diatonic_keys.append(('weight', weight, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
            
        else:
            
            if KEY_PADS[first_chromatic]:
                weight = (KEY_PADS[first_chromatic]/2) + int(show_octave)
                chromatic_keys.append(('weight', weight, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
            
            if not KEY_PADS[first_chromatic]:
                if not show_octave:
                    weight = 0.5 + KEY_PADS[first_chromatic] + int(show_octave)
                    diatonic_keys.append(('weight', weight, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))
                else:
                    weight = 0.5 #+ KEY_PADS[first_chromatic] + int(show_octave)
                    chromatic_keys.append(('weight', weight, urwid.BoxAdapter(urwid.SolidFill(SPACE_CHAR),height=1)))

        chromatic = urwid.Columns(widget_list=chromatic_keys, dividechars=1)
        diatonic = urwid.Columns(widget_list=diatonic_keys, dividechars=1)
        
        keyboard = urwid.Pile([chromatic, diatonic])
        box = urwid.LineBox(keyboard)
        
        super(Keyboard, self).__init__(body=box, min_height=6, *args, **kwargs)
    
    def highlight_key(self, note):
        #print('were in highlight_key')
        for key, button in self.key_index.items():
            #from pprint import pprint
            state = key==note
            if 'KeyboardButton' in str(type(button)):
                button.highlight(state=state)
        


class TextUserInterface(urwid.Frame):

    def __init__(self, exercise, *args, **kwargs):

        self.question = self.create_question(exercise=exercise, **kwargs)
        
        self.input_keys = list()
        
        kwargs = {
            'callback': None,
            'end_callback': None
        }
        
        thread = threading.Thread(target=self.question.play_question, kwargs=kwargs)
        thread.start()
        #self.question.play_question()
        self.draw(self.question)
        #self.question.play_question()
        #thread = self.question.pre_question.play()
        #thread.join()
        #thread = self.question.question.play()
        #thread.join()
        
        #loop = urwid.MainLoop(self)
        #loop.run()
        
    def keypress(self, size, key):
        
        if key in self.question.keyboard_index and key != ' ': # space char
            self.input_keys.append(key)

            #if exercise == 'dictation':
            #    input_str = make_input_str(input_keys, question.keyboard_index)
            #    #print(input_str, end='')

            #if len(input_keys) == dictate_notes:

            response = self.question.check_question(self.input_keys)
            #print_response(response)

            kwargs = {
                'callback': None,
                'end_callback': None
            }
            
            thread = threading.Thread(target=self.question.play_resolution, kwargs=kwargs)
            thread.start()
            # self.question.play_resolution()

        elif key in ('T', 't'):
            # self.frame_body.contents[1] = (urwid.Text('hey'), ('pack', None))
            #print(self.frame_body.contents[1][0].key_index)
            #print(self.frame_body.contents)
            self.frame_body.contents[1][0].highlight_key('C')
        elif key in ('R', 'r'):
            self.question.play_question()
        elif key in ('Q', 'q'):
            raise urwid.ExitMainLoop()
        else:
            pass
        
        #self.keyboard = Keyboard(tonic='D')
        
    def create_question(self, exercise, **kwargs):
        
        if exercise in QUESTION_CLASSES:
            QUESTION_CLASS = QUESTION_CLASSES[exercise]
        else:
            raise Exception("Oops!", QUESTION_CLASSES)
            
        if 'n_notes' in kwargs:
            dictate_notes = kwargs['n_notes']
        else:
            dictate_notes = 1
        
        return QUESTION_CLASS(**kwargs)
        
    def draw(self, question):
        
        self.header = urwid.Text('hey pal')
        self.footer = urwid.Text('footers')

        self.keyboard = Keyboard(tonic='C')
        self.keyboard = Keyboard(question.tonic_str)
        
        self.top_widget = urwid.Filler(urwid.LineBox(urwid.Text('test1\nok')))
        self.bottom_widget = urwid.Filler(urwid.LineBox(urwid.Text('test2')))
        
        self.frame_elements = [self.top_widget, self.keyboard, self.bottom_widget]
        
        self.frame_body = urwid.Pile(widget_list=self.frame_elements)
        self.frame_body_pad = urwid.Padding(self.frame_body, align='center', width=('relative', 60))

        super(TextUserInterface, self).__init__(body=self.frame_body_pad, header=self.header, footer=self.footer)
