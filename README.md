======== FFT Conditional Compiler =======
1)  Under the Battle and World menu options, you can compile a .txt file or a folder containing .txt files that
        FFT Conditional Compiler will read to create the new conditionals.
    You after selecting, you will be prompted to select the file or folder that will be compiled and the name of the .xml file that
        will be saved as. This xml file is meant to be read by FFTorgASM to apply the data to your Final Fantasy Tactics bin/iso file.

2)  If you're using some of the custom event conditional instructions, like Xifanie's Defeat() instruction,
    click the 'Use Expanded Conditionals' under the File menu otherwise this program will ignore the instructions.
    
3)  You are able to use labels (or constants whichever terminology you prefer) to use the labels instead of value.
    Update the labels.json file in the json_files folder to create your own labels.
    Alternatively you can create a new json file and update the config.json file in the json_files folder to the
        name of the new json file.

4)  Below is the format of the vanilla Event Conditionals and World Conditionals with some labels used.
    'ConditionalID' tells FFT Conditional Compiler that is a new set of conditionals.
    'Entry' tells FFT Conditional Compiler that the next lines will be instructions to be encoded for this conditional,
        using 'Entry' again will tell FFT Conditional Compiler to end the previous set of instructions for a new set.
    All of the information for the instructions can be found in the event_instructions.json and world_instructions.json
        located in the json_files folder.
        
        
        === BATTLE CONDITIONALS ====                    === WORLD CONDITIONALS ===
        ConditionalID: x000                             CONDITIONALID: x00
            Entry:                                          Entry: x01
                Var=(x01FD, 1)                                   Var=(x06E, x20)
                LoadEvent(x002)                                 LoadEvent(x0DF, x02)
                                                        
        ConditionalID: x001                                 Entry: x02
            Entry:                                              Var=(StoryProgression, x21)
                Var=(x01FD, true)                               LoadEvent(x0E1, x01)
                LoadEvent(x004)                         
                                                            Entry: x03
            Entry:                                              Var=(x23F, false)
                Var=(x07F, x000)                                Var=(StoryProgression, x22)
                Var=(x080, x000)                                DrawPath(x09, x12)
                Present(Gafgarion)                      
                Present(Agrias)                             Entry: x04
                ActiveTurn(Agrias)                              Var=(x212, false)
                UnitHP>=(Gafgarion, 1)                          Var=(StoryProgression, x22)
                UnitHP>=(Agrias, 1)                             DrawLocation(x12)
                LoadEvent(x005)                         
                                                            Entry: x05
            Entry:                                              Var=(x099, true)
                Var=(x080, false)                               Var=(x0A6, true)
                Victory()                                       Var=(x0A7, false)
                LoadEvent(x006)                                 LoadEvent(x1D0, x02)
                                                        
        ConditionalID: x002                             CONDITIONALID: x01
            Entry:                                          Entry:
                LoadEvent(x008)                                 Var=(StoryProgression, x0028)                        
                                                                Choice(0x0006,0x0112,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000)
