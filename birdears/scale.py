from . import DIATONIC_MODES
from . import CHROMATIC_SHARP
from . import CHROMATIC_FLAT

from .note_and_pitch import Note
from .note_and_pitch import Pitch

from .note_and_pitch import get_pitch_class

from .exception import InvalidNote

# https://docs.python.org/3/reference/datamodel.html#emulating-container-types

class ScaleBase(list):
    def __init__(self):
        pass

    def _append_octave_to_scale(self, scale, starting_octave, descending=None):
        """Inserts scientific octave number to the notes on a the given scale.
        """

        next_octave = 1 if not descending else -1

        scale_with_octave = []
        changing_note = None

        current_octave = starting_octave

        # if scale doesn't have a C, on which note should we go to the upper/lower octave?
        # TODO: need to be refactored. Maybe using the pitch number.
        if not descending:
            for closest in ['C', 'C#', 'Db']:
                if closest in scale:
                    changing_note = closest
                    break
        else:
            for closest in ['B', 'Bb', 'A#']:
                if closest in scale:
                    changing_note = closest
                    break

        for idx, note in enumerate(scale):
            if idx > 0 and note == changing_note:
                current_octave += next_octave

            # scale_with_octave.append("{}{}".format(note, current_octave))
            scale_with_octave.append(Pitch(note=note, octave=current_octave))
            
        return scale_with_octave

    #def _get_chromatic_idx(self, note):
    #    """Gets the chromatic index, ie., the distance in semitones of a given
    #    note from C.
    #    """
    #
    #    global CHROMATIC_SHARP, CHROMATIC_FLAT
    #
    #    if note in CHROMATIC_SHARP:
    #        note_index = CHROMATIC_SHARP.index(note)
    #    elif note in CHROMATIC_FLAT:
    #        note_index = CHROMATIC_FLAT.index(note)
    #    else:
    #        raise InvalidNote
    #
    #    return note_index

    #def _rotate_scale_by_idx(self, index, scale):
    #    """Rotates chromatic C scale to generate another chromatic based on
    #    index number of the tonic.
    #    """
    #
    #    idx_to_end = slice(index, None)
    #    begin_to_idx = slice(None, index)
    #
    #    rotated_scale = []
    #    rotated_scale.extend(scale[idx_to_end])
    #    rotated_scale.extend(scale[begin_to_idx])
    #
    #    return rotated_scale


class DiatonicScale(ScaleBase):
    """Builds a musical diatonic scale.

    Attributes:
        scale (array_type): The array of notes representing the scale.
    """

    def __init__(self, tonic, mode='major', octave=None, n_octaves=None,
                 descending=None, dont_repeat_tonic=None):
        """Returns a diatonic scale from tonic and mode.

        Args:
            tonic (str): The note which the scale will be built upon.
            mode (str): The mode the scale will be built upon.
                ('major' or 'minor')
            octave (int): The scientific octave the scale will be built upon.
            n_octaves (int): The number of octaves the scale will contain.
            descending (bool): Whether the scale is descending.
            dont_repeat_tonic (bool): Whether to skip appending the last
                note (octave) to the scale.
        """

        super(DiatonicScale, self).__init__()

        global DIATONIC_MODES

        self.tonic = tonic
        self.mode = mode
        self.octave = octave
        self.direction = "Ascending" if not descending else "Descending"

        diatonic_mode = DIATONIC_MODES[mode]

        chromatic = ChromaticScale(tonic=tonic)

        diatonic = [chromatic[semitones] for semitones in diatonic_mode[:-1]]

        if n_octaves:
            diatonic = diatonic * n_octaves

        # FIXME: check if this works on descending
        if not dont_repeat_tonic:
            diatonic.append(chromatic[diatonic_mode[-1]])

        if descending:
            diatonic.reverse()

        if octave:
            diatonic = self._append_octave_to_scale(scale=diatonic,
                                                    starting_octave=octave,
                                                    descending=descending)

        #self.scale = diatonic
        self.extend(diatonic)

    # FIXME: aybe ake this a function
    def get_triad(self, index=0, degree=None):
        """Returns an array with notes from a scale's triad.

        Args:
            index (int): triad index (eg.: 0 for 1st degree triad.)
            degree (int): Degree of the scale. If provided, overrides the
                `index` argument. (eg.: `1` for the 1st degree triad.)
        Returns:
            An array with three pitches, one for each note of the triad.
        """

        global DIATONIC_MODES

        tonic = self.tonic
        mode = self.mode
        octave = self.octave

        diatonic_mode = DIATONIC_MODES[mode]

        chromatic = ChromaticScale(tonic=tonic)

        diatonic = [chromatic[semitones] for semitones in diatonic_mode[:-1]]

        diatonic = diatonic * 2

        # FIXME: check if this works on descending
        diatonic.append(chromatic[diatonic_mode[-1]])

        octave = self.octave or 4
        diatonic = self._append_octave_to_scale(scale=diatonic,
                                                starting_octave=octave,
                                                descending=False)

        self.scale = diatonic
        if degree:
            index = degree - 1

        form = [0, 2, 4]

        triad = [diatonic[index+note] for note in form]

        return triad

    def __repr__(self):
        
        repr = "<DiatonicScale {tonic} {mode} {direction} {first}-{to} " \
               "({octaves} octaves)>" \
                   .format(tonic=str(self[0].note),
                           mode=self.mode.capitalize(),
                           direction=self.direction.capitalize(),
                           first=str(self[0]),
                           to=str(self[-1]), octaves=int(len(self)/8))
        return repr
    
    def __str__(self):
        return str(list(self))

class ChromaticScale(ScaleBase):
    """Builds a musical chromatic scale.

    Attributes:
        scale (array_type): The array of notes representing the scale.
    """

    def __init__(self, tonic='C', octave=4, n_octaves=1, descending=False,
                 dont_repeat_tonic=False):
        """Returns a chromatic scale from tonic.

        Args:
            tonic (str): The note which the scale will be built upon.
            octave (int): The scientific octave the scale will be built upon.
            n_octaves (int): The number of octaves the scale will contain.
            descending (bool): Whether the scale is descending.
            dont_repeat_tonic (bool): Whether to skip appending the last
                note (octave) to the scale.
        """

        super(ChromaticScale, self).__init__()

        global CHROMATIC_SHARP, CHROMATIC_FLAT

        self.tonic = Pitch(tonic, octave)
        #self.octave = octave

        pitch_class = get_pitch_class(tonic)

        chromatic = tuple(CHROMATIC_FLAT) if (tonic == 'F' or 'b' in tonic) \
                    else tuple(CHROMATIC_SHARP)
        
        # let's rotate the scale
        chromatic = chromatic[pitch_class:] + chromatic[:pitch_class]
            
        scale = [Note(note=note) for note in chromatic]
        scale *= n_octaves
        
        direction = 1 if not descending else -1
        
        tonic_pitch_number = int(self.tonic)
        self = [Pitch().get_pitch_by_number(tonic_pitch_number + i) 
                for i in range(12 * n_octaves)]
            
            
        
        # FIXME: check if this works on descending
        
        if not dont_repeat_tonic:
            self.append(self[0])

        #if descending:
        #    self.reverse()

        #if octave:
        #    scale = self._append_octave_to_scale(scale=scale,
        #                                         starting_octave=octave,
        #                                         descending=descending)

        #self.extend(scale)

    def get_triad(self, mode, index=0, degree=None):
        """Returns an array with notes from a scale's triad.

        Args:
            mode (str): Mode of the scale (eg. 'major' or 'minor')
            index (int): Triad index (eg.: 0 for 1st degree triad.)
            degree (int): Degree of the scale. If provided, overrides the
                `index` argument. (eg.: `1` for the 1st degree triad.)
        Returns:
            A list with three pitches (str), one for each note of the triad.
        """

        global DIATONIC_MODES

        tonic = self.tonic
        octave = self.octave

        diatonic_mode = DIATONIC_MODES[mode]

        chromatic = ChromaticScale(tonic)

        diatonic = [chromatic[semitones] for semitones in diatonic_mode[:-1]]

        diatonic = diatonic * 2

        # FIXME: check if this works on descending
        diatonic.append(chromatic[diatonic_mode[-1]])

        octave = self.octave or 4
        diatonic = self._append_octave_to_scale(scale=diatonic,
                                                starting_octave=octave,
                                                descending=False)

        self.scale = diatonic
        if degree:
            index = degree - 1

        form = [0, 2, 4]

        triad = [diatonic[index+note] for note in form]

        return triad
