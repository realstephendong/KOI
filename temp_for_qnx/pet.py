from temp_for_qnx.parse_for_qnx import load_1bit_bmp


class Pet:
    def __init__(self, animation_state, hp, hearts):
        self.animation_state = animation_state
        self.hp = hp
        self.hearts = hearts

        self.curr_frame = 0

    def create_pet_frames(self, pet_choice):
        if (pet_choice == "koi"):            
            pet_frames = {
                "idle": [
                    load_1bit_bmp("soy_idle0.bmp")[0],
                    load_1bit_bmp("soy_idle1.bmp")[0]
                ],
                # "sad": [
                #     load_1bit_bmp("soy_sad0.bmp")[0],
                #     load_1bit_bmp("soy_rsad1.bmp")[0]
                # ]
            }

            return pet_frames
        
        # elif (pet_choice == "soy"):
        # elif (pet_choice --  'koi"):
    

    