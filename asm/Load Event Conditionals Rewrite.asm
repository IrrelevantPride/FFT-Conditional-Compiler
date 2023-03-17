                        # 0x800475e0 = SCUS space for the half-word pointers leading to each set of conditionals
                        # 0x80049a18 - SCUS space for the instruction data

                        .label  @LoadSector, 0x80044954

                        move    s1, v0                              # eventScriptID
                        la      a0, 0x00014B08                      # start = 0x00014b08
                        la      a2, 0x801df000                      # location = 0x801df000
                        jal     @LoadSector                         # LoadSector(start, size, location)
                        lui     a1, 0x0001                          # size = 0x00010000
                        la      a0, 0x800475e0                      # scuc_eventScript.set_pointers
                        sll     v0, s1, 1                           # eventScriptID * 2
                        la      a1, 0x801d3938                      # start of attack.out scenario pointers
                        addu    v1, v0, a1                          # eventScript scenario pointer
                        lhu     v0, 0(v1)                           # eventScript.scenario_pointer
                        nop                                         #
                        addu    t0, v0, a1                          # 0x80d3938 + eventScript.scenario_pointer 
                        lhu     t1, 0(t0)                           # eventScript.set_pointer
setLoop:                                                            # for counter in range(16):
                        lhu     v0, 0(t0)                           #   current_eventScript.set_pointer
                        nop                                         # 
                        subu    v1, v0, t1                          #   current_eventScript.set_pointer - eventScript.set_pointer
                        sh      v1, 0(a0)                           #   scus_eventScript.set_pointers[counter * 2]
                        bnez    v0, continue                        #   if not current_eventScript.set_pointer:
                        nop                                         #   
                        j       break                               #
                        sh      zero, 0(a0)                         #   store 0
continue:               addiu   t0, t0, 2                           #   *current_eventScript.set_pointer += 2
                        addiu   s0, s0, 1                           #   counter ++
                        slti    v0, s0, 16                          # 
                        bne     v0, zero, setLoop                   # 
                        addiu   a0, a0, 2                           #   *scus_eventScript.set_pointers += 2
break:                  li      s0, 0                               # counter = 0
                        lhu     a0, 0x800475e0                      # scus.eventScript.set_pointers
                        la      a1, 0x80049a18                      # scus.eventScript.instruction_data
                        la      a2, 0x801DF000                      # instructionStart
instructionLoop:                                                    # for counter in range(256)
                        sll     v1, s0, 1                           #   counter * 2
                        addu    v0, a0, a2                          #   instructionStart + scus_eventScript.set_pointer
                        addu    v0, v0, t1                          #   instructionStart + current_eventScript.set_pointer + 
                        addu    v0, v0, v1                          #   instructionStart + current_eventScript.set_pointer + (counter * 2)
                        lhu     v0, 0(v0)                           #   current_eventScript.instruction_data[counter]
                        addiu   s0, s0, 1                           #   counter ++
                        sh      v0, 0(a1)                           #   scus_eventScript.instruction_data[counter] = current_eventScript.instruction_data[counter]
                        slti    v0, s0, 512                         # 
                        bne     v0, zero, instructionLoop           # 
                        addiu   a1, a1, 2                           # 
                        nop                                         # 
                        nop                                         #
        