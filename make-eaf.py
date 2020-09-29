from pympi.Elan import Eaf
from typing import Dict, List, Union, Type

"""
This script builds an Elan file using tiers from two input files.

File 1 includes a phrase transcription and free translation of a text.
File 2 includes the free translation that has been exported to FLEx, interlinearized, and then imported back into ELAN.
File 3 is the result. 

OMG.... probably would have been simpler to do this by parsing the XML. 
The complexities of this script are due to the hierarchies in the input files. 
Anyway, it was an interesting exercise in using pympi-ling. 

Requires patched version of Pympi-ling to get top-tier in a hierarchy of ref tiers when doing add_ref_annotation.
pip install git+https://github.com/dopefishh/pympi.git@57518a0fb646037c09f925ca3aa08b29cd20725a
BTW, This script won't run in PyCharm due to this custom pip install. Gotta do it in Terminal.
"""


def get_info(eaf: Type[Eaf]):
    """
    Just a handy helper to show info about a tier

    :param eaf: an Elan object
    :return:
    """
    type_names = eaf.get_linguistic_type_names()
    print("type_names", type_names)

    for type_name in eaf.get_linguistic_type_names():
        phrases_type_params = eaf.get_parameters_for_linguistic_type(type_name)
        print("type:", type_name, phrases_type_params)

    tier_names = eaf.get_tier_names()
    for tier_name in tier_names:
        params = eaf.get_parameters_for_tier(tier_name)
        print("tier:", tier_name, params)


def copy_media(eaf_1: Type[Eaf], eaf_3: Type[Eaf]):
    """
    Copy the media file info from file 1 into the new file

    :param eaf_1: Source Eaf object which has the media linked file
    :param eaf_3: Destination Eaf object
    :return:
    """
    # Get all the media for the first file
    media = eaf_1.media_descriptors
    # Get params for first media item, unpack into vars
    media_params = sorted(media[0].items())
    file_path, mimetype, relpath = [v[1] for v in media_params]
    eaf_3.add_linked_file(file_path, mimetype=mimetype, relpath=relpath)
    return eaf_3


def _tier_copy(source_eaf: Type[Eaf] = None,
               target_eaf: Type[Eaf] = None,
               source_tier_name: str = "",
               target_tier_name: str = "",
               override_params: Dict[str, str] = {}):
    """
    Straight up copy of a non-ref tier from one Eaf object to a new Eaf object

    :param source_eaf: The Eaf object to copy from
    :param target_eaf: The Eaf object to write to
    :param source_tier_name: Name of the tier to get
    :param target_tier_name: The name to call this tier in the destination
    :param override_params: Use this to change tier params from what the tier has in the source file
    :return:
    """
    # For tier params, use the passed in dict or read from source
    params = override_params if override_params else source_eaf.get_parameters_for_tier(source_tier_name)
    # Add new tier in target file
    target_eaf.add_tier(target_tier_name, ling=params["LINGUISTIC_TYPE_REF"], tier_dict=params)
    # Read annotations from source
    annotations = source_eaf.get_annotation_data_for_tier(source_tier_name)
    # Write each annotation to target
    for annotation in annotations:
        target_eaf.add_annotation(id_tier=target_tier_name,
                                  start=annotation[0],
                                  end=annotation[1],
                                  value=annotation[2])
    return target_eaf


def _ref_tier_copy(source_eaf: Type[Eaf] = None,
                   target_eaf: Type[Eaf] = None,
                   source_tier_name: str = "",
                   target_tier_name: str = "",
                   target_parent_tier_name: str = "",
                   override_params: Dict[str, str] = {}):
    """
    Copy annotations from a ref tier in one EAF to a new ref tier in another EAF

    :param source_eaf: The Eaf object to copy from
    :param target_eaf: The Eaf object to write to
    :param source_tier_name: Name of the tier to get
    :param target_tier_name: The name to call this tier in the destination
    :param target_parent_tier_name: The name of the parent for the ref tier in the destination object
    :param override_params: Use this to change tier params from what the tier has in the source file
    :return:
    """
    params = override_params if override_params else source_eaf.get_parameters_for_tier(source_tier_name)
    target_eaf.add_tier(target_tier_name, ling=params["LINGUISTIC_TYPE_REF"], parent=target_parent_tier_name, tier_dict=params)
    annotations = source_eaf.get_ref_annotation_data_for_tier(source_tier_name)
    for annotation in annotations:
        target_eaf.add_ref_annotation(id_tier=target_tier_name,
                                      tier2=target_parent_tier_name,
                                      time=annotation[0]+1,
                                      value=annotation[2])
    return target_eaf


def _tier_copy_to_ref(source_eaf: Type[Eaf] = None,
                      target_eaf: Type[Eaf] = None,
                      source_tier_name: str = "",
                      target_tier_name: str = "",
                      target_parent_tier_name: str = "",
                      override_params: Dict[str, str] = {}):
    """
    Copy a non-ref tier, but make it a ref tier in the destination

    :param source_eaf: The Eaf object to copy from
    :param target_eaf: The Eaf object to write to
    :param source_tier_name: Name of the tier to get
    :param target_tier_name: The name to call this tier in the destination
    :param target_parent_tier_name: The name of the parent for the ref tier in the destination object
    :param override_params: Use this to change tier params from what the tier has in the source file
    :return:
    """
    params = override_params if override_params else source_eaf.get_parameters_for_tier(source_tier_name)
    target_eaf.add_tier(target_tier_name, ling=params["LINGUISTIC_TYPE_REF"], parent=target_parent_tier_name, tier_dict=params)
    annotations = source_eaf.get_annotation_data_for_tier(source_tier_name)
    for annotation in annotations:
        target_eaf.add_ref_annotation(id_tier=target_tier_name,
                                      tier2=target_parent_tier_name,
                                      time=annotation[0],
                                      value=annotation[2])
    return target_eaf


def _copy_symbolic_subdivision_tier(source_eaf: Type[Eaf] = None,
                                    target_eaf: Type[Eaf] = None,
                                    source_tier_name: str = "",
                                    target_tier_name: str = "",
                                    target_parent_tier_name: str = "",
                                    override_params: Dict[str, str] = {}):
    """
    Copy annotations from a SYMBOLIC SUBDIVISION ref tier in one EAF to a new ref tier in another EAF
    Symbolic Subdivisions spread ref annotations evenly across the timespan of the parent annotation.
    For a symbolic subdivision type tier, the annotations in each group need to refer to their previous
    (except the first one in the group)

    :param source_eaf: The Eaf object to copy from
    :param target_eaf: The Eaf object to write to
    :param source_tier_name: Name of the tier to get
    :param target_tier_name: The name to call this tier in the destination
    :param target_parent_tier_name: The name of the parent for the ref tier in the destination object
    :param override_params: Use this to change tier params from what the tier has in the source file
    :return:
    """
    params = override_params if override_params else source_eaf.get_parameters_for_tier(source_tier_name)
    target_eaf.add_tier(target_tier_name, ling=params["LINGUISTIC_TYPE_REF"], parent=target_parent_tier_name, tier_dict=params)
    annotations = source_eaf.get_ref_annotation_data_for_tier(source_tier_name)
    previous_parent_id = None
    previous_id = None
    for annotation in annotations:
        prev = previous_id if annotation[3] == previous_parent_id else None
        target_eaf.add_ref_annotation(id_tier=target_tier_name,
                                      tier2=target_parent_tier_name,
                                      time=annotation[0]+1,
                                      value=annotation[2],
                                      prev=prev)

        previous_parent_id = annotation[3] if len(annotation) >= 3 else None
        previous_id = f"a{target_eaf.maxaid}"

    return target_eaf


def main():
    """
    File 1 has the utterance and utterance translation
    File 2 has the gloss
    File 3 is the destination
    """
    # Input files
    file_1 = 'input/file-1.eaf'
    file_2 = 'input/file-2.eaf'
    file_3 = 'input/new.eaf'

    # Tier names
    utterance_id_source_tier = "A_phrase-segnum-en"
    utterance_id_target_tier = "utterance_id"
    utterance_source_tier = "DDD_Transcription-txt-qaa-fonipa-x-eib"
    utterance_target_tier = "utterance"
    utterance_translation_source_tier = "DDD_Translation-gls-en"
    utterance_translation_target_tier = "utterance_translation"
    word_source_tier = "A_word-txt-qaa-fonipa-x-eib"
    word_target_tier = "grammatical_words"
    morph_source_tier = "A_morph-txt-qaa-fonipa-x-eib"
    gloss_source_tier = "A_morph-gls-en"
    gloss_target_tier = "gloss"

    # Set up the eaf objects
    eaf_1 = Eaf(file_1)
    eaf_2 = Eaf(file_2)
    eaf_3 = Eaf()

    # Remove default tier and copy media
    eaf_3.remove_tier("default")
    # eaf_3 = copy_media(eaf_1, eaf_3)

    """
    Copy annotation number tier from file 2
    tier-type default-lt
    <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="default-lt" TIME_ALIGNABLE="true"/>
    """
    print("Copying annotation numbers from file 2")
    utterance_id_type_params = {'LINGUISTIC_TYPE_ID': 'default-lt', 'TIME_ALIGNABLE': 'true'}
    utterance_id_tier_params = {'LINGUISTIC_TYPE_REF': 'default-lt', 'TIER_ID': utterance_id_target_tier}
    _tier_copy(source_eaf=eaf_2,
               target_eaf=eaf_3,
               source_tier_name=utterance_id_source_tier,
               target_tier_name=utterance_id_target_tier,
               override_params=utterance_id_tier_params)

    """
    Copy utterance tier from file 1
    LINGUISTIC_TYPE_REF="Blank"
    <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Association" GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="Blank" TIME_ALIGNABLE="false"/>
    """
    print("Copying utterance tier from file 1")
    blank_type_params = {'LINGUISTIC_TYPE_ID': 'Blank', 'CONSTRAINTS': 'Symbolic_Association', 'TIME_ALIGNABLE': 'false'}
    eaf_3.add_linguistic_type('Blank', param_dict=blank_type_params)
    utterance_tier_params = {'LINGUISTIC_TYPE_REF': 'Blank', 'PARENT_REF': utterance_id_target_tier, 'TIER_ID': utterance_target_tier}
    _tier_copy_to_ref(source_eaf=eaf_1,
                      target_eaf=eaf_3,
                      source_tier_name=utterance_source_tier,
                      target_tier_name=utterance_target_tier,
                      target_parent_tier_name=utterance_id_target_tier,
                      override_params=utterance_tier_params)

    """
    Copy utterance translation tier from file 1
    LINGUISTIC_TYPE_REF="Blank"
    <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Association" GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="Blank" TIME_ALIGNABLE="false"/>
    <TIER LINGUISTIC_TYPE_REF="Blank" PARENT_REF="utterance" PARTICIPANT="DDD" TIER_ID="utterance_translation">    
    """
    print("Copying utterance translation tier from file 1")
    utterance_translation_tier_params = {'LINGUISTIC_TYPE_REF': 'Blank', 'PARENT_REF': utterance_target_tier, 'TIER_ID': utterance_translation_target_tier}
    _ref_tier_copy(source_eaf=eaf_1,
                   target_eaf=eaf_3,
                   source_tier_name=utterance_translation_source_tier,
                   target_tier_name=utterance_translation_target_tier,
                   target_parent_tier_name=utterance_target_tier,
                   override_params=utterance_translation_tier_params)

    """
    Copy the word tier from file 2
        <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Subdivision" GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="word" TIME_ALIGNABLE="false"/>
        <TIER DEFAULT_LOCALE="qaa-fonipa-x-eib" LINGUISTIC_TYPE_REF="word" PARENT_REF="A_phrase-segnum-en" PARTICIPANT="DDD" TIER_ID="A_word-txt-qaa-fonipa-x-eib">

    """
    print("Copying word tier from file 2")
    word_type_params = {'LINGUISTIC_TYPE_ID': 'word', 'CONSTRAINTS': 'Symbolic_Subdivision', 'TIME_ALIGNABLE': 'false'}
    eaf_3.add_linguistic_type('word', param_dict=word_type_params)

    word_tier_params = {'LINGUISTIC_TYPE_REF': 'word', 'PARENT_REF': utterance_target_tier, 'TIER_ID': word_target_tier}

    _copy_symbolic_subdivision_tier(source_eaf=eaf_2,
                                    target_eaf=eaf_3,
                                    source_tier_name=word_source_tier,
                                    target_tier_name=word_target_tier,
                                    target_parent_tier_name=utterance_id_target_tier,
                                    override_params=word_tier_params)

    """
    Get all the annotations from -2 gloss tier (gloss_source_tier A_morph-gls-en)
    Join the glosses with "-" so there is a 1:1 match with word annotations
    <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Association" GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="Blank" TIME_ALIGNABLE="false"/>
    <TIER LINGUISTIC_TYPE_REF="Blank" PARENT_REF="grammatical_words" TIER_ID="gloss">
    """
    print("Epic battle with words to get glosses from file 2")
    gloss_tier_params = {'LINGUISTIC_TYPE_REF': 'Blank', 'PARENT_REF': word_target_tier, 'TIER_ID': gloss_target_tier}
    # None of the pympi methods will suit this task, so let's do it manually.
    # Get all the data
    eaf_2_tiers = eaf_2.tiers
    eaf_2_timeslots = eaf_2.timeslots
    # A tier is of the form: {tier_name -> (aligned_annotations, reference_annotations, attributes, ordinal)},
    # Word and gloss tiers are ref_annotations, the second item in the tiers dict. See docs for more info about format.
    word_tier = eaf_2_tiers[word_source_tier][1]
    morph_tier = eaf_2_tiers[morph_source_tier][1]
    gloss_tier = eaf_2_tiers[gloss_source_tier][1]

    # Each reference annotation is of the form: [{id -> (reference, value, previous, svg_ref)}].
    # Start at the top of the hierarchy
    utterance_id_tier = eaf_2_tiers[utterance_id_source_tier][0]

    new_dict = dict()
    # For each utterance, get the words. For each word, get the glosses. Merge glosses for each word
    for utterance_id, utterance in utterance_id_tier.items():
        utt_start = eaf_2_timeslots[utterance[0]]
        utt_end = eaf_2_timeslots[utterance[1]]
        word_gloss: List[Union[int, List[str]]] = []
        for word_id, word in word_tier.items():
            if word[0] == utterance_id:
                glosses = []
                # Find morphs of this word...
                for morph_id, morph in morph_tier.items():
                    # ...by filtering on morph parents id matching the word id
                    if morph[0] == word_id:
                        for gloss_id, gloss in gloss_tier.items():
                            if gloss[0] == morph_id:
                                glosses.append(gloss[1])
                # Join glosses for this word with a dash
                word_gloss.append([word[1], '-'.join(glosses)])
        # Now, work out word duration (it is an even division of parent utterance duration)
        # Make this value the first item in the data list eg [word_duration, [word, gloss], [word, gloss], ...]
        num_segments = len(word_gloss)
        utt_dur = utt_end - utt_start
        word_dur = int(utt_dur / num_segments)
        word_gloss = [utt_start, word_dur] + word_gloss

        new_dict[utterance_id] = word_gloss

    # Having worked all that out, now we can add a ref annotation tier.
    # but parent seems to now bubble all the way to the top.
    eaf_3.add_tier(gloss_target_tier, ling='Blank', parent=word_target_tier, tier_dict=gloss_tier_params)
    # And some annotations
    for ann_id, annotation in new_dict.items():
        utt_start = annotation[0]
        word_dur = annotation[1]
        count = 0

        for ann in annotation[2:]:
            word_start = utt_start + word_dur * count
            id_tier = gloss_target_tier
            tier2 = word_target_tier
            value = ann[1]
            prev = None
            svg = None

            for aid, (ref_id, _value, _prev, _) in eaf_3.tiers[tier2][1].items():
                if ann[0] == _value:
                    new_aid = eaf_3.generate_annotation_id()
                    eaf_3.tiers[id_tier][1][new_aid] = (aid, value, prev, svg)

            count = count + 1

    # Save the new file
    print("Saving object to file")
    eaf_3.to_file(file_3)


if __name__ == "__main__":
    main()
