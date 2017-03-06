c  -------------------------------  CELL CARD  ------------------------------  c
c  Core level           
c    Core Shroud                 
600 80000 -8.0 ((-802 -602 603 604):(601 -604 -602 605)) imp:n=1    $Core_shroud
c    Core Water                  
700 1 -0.998207 ((-802 602 -803):(803 -805):(-602 501 -601):(-603    $Core Level
          501 -802 604):(-605 -802 804):(-804 -802 -807)) imp:n=1     $Core Level
c    Active Core                 
10000000 10000000 0.035555 (-501 -601 605) imp:n=1 vol=21205750     $Active Fuel
50000000 50000000 0.035555 (-606 605 604 -501) imp:n=1 vol=26507188 $Active Fuel
c    Reflector Region            
650 2 -1.7 -802 606 -501 605 imp:n=1                                  $reflector
c
c  Reactor level        
800 80000 -8.0 ((-801 802 -803 804):(-806 805 803):(-808 807    $Pressure Vessel
          -804)) imp:n=1                                         $Pressure Vessel
c
c  Shielding            
900 90000 -2.3 -900 801 -902 903 806 imp:n=1                 $Concrete Shielding
901 1 -0.998207 ((-801 806 -902 803):(-801 808 903 -804))       $Water Shielding
          imp:n=1                                                $Water Shielding
c
c  Outside World level  
990 0 (-903:902:(900 903 -902)) imp:n=0                           $Outside World

c  -----------------------------  SURFACE CARD  -----------------------------  c
c  Core level           
c    Core Shroud                  
601 CZ 100                                                      $TC_shroud_inner
602 PZ 201                                              $Shroud_upper_extent_top
603 PZ 200                                           $Shroud_upper_extent_bottom
604 CZ 101                                                      $TC_shroud_outer
605 PZ -150                                                       $Shroud_bottom
c                                 
501 PZ 150                                                    $Upper Active Core
c                                 
606 CZ 176                                                   $Graphite reflector
c
c  Reactor level        
801 CZ 276                                                             $Outer_PV
802 CZ 226                                                             $Inner_PV
803 PZ 600                                                  $PV_cyl_upper_extent
804 PZ -300                                                 $PV_cyl_lower_extent
805 S 0 0 600 226                                             $Inner_dome_sphere
806 S 0 0 600 276                                             $Outer_dome_sphere
807 S 0 0 -300 226                                            $Inner_dome_sphere
808 S 0 0 -300 276                                            $Outer_dome_sphere
c
c  Shielding level      
900 CZ 576                                                     $Outer_shield_cyl
901 CZ 276                                                     $Inner_shield_cyl
902 PZ 1350                                                  $Upper_shield_plane
903 PZ -650                                                  $Lower_shield_plane
 
c  -------------------------------  DATA CARD  ------------------------------  c
c  Burnup Card
c                       
burn  time=54.75 9R power=1 pfrac=9R bopt=1 14 -1                  $Burnup_input
      mat=10000000 50000000                                            $burn_mat
      omit= -1 98  66159 67163 67164 67166 68163 68165 68169 69166    $burn_omit
         69167 69171 69172 69173 70168 70169 70170 70171 70172 70173  $burn_omit
         70174 6014 7016 39087 39092 39093 40089 40097 41091 41092    $burn_omit
         41096 41097 41098 41099 42091 42093 70175 70176 71173 71174  $burn_omit
         71177 72175 72181 72182 73179 73183 74179 74181 8018 8019    $burn_omit
         9018 10021 12027 13026 13028 14027 14031 16031 16035 16037   $burn_omit
         17034 17036 17038 18037 18039 22051 23047 23048 23049 23052  $burn_omit
         23053 23054 24049 24051 24055 24056 25051 25052 25053 25054  $burn_omit
         25056 25057 25058 26053 26055 26059 26060 26061 27057 27060  $burn_omit
         27061 27062 27063 27064 28057 28063 28065 29062 29064 29066  $burn_omit
c
c  MATERIAL             
c    Material Data                 
C name: Carbon, Graphite (reactor grade)
C density = 1.7
m2
     5010 -1.8431e-07
     5011 -8.1569e-07
     6012 -9.8841e-01
     6013 -1.1584e-02
 mt2        grph.20t                                           $Thermal Treatment
C name: Steel, Stainless 304
C density = 8.0
m80000
     6012 -3.9536e-04
     6013 -4.6337e-06
     14028 -4.5933e-03
     14029 -2.4168e-04
     14030 -1.6499e-04
     15031 -2.3000e-04
     16032 -1.4207e-04
     16033 -1.1568e-06
     16034 -6.7533e-06
     16036 -1.6825e-08
     24050 -7.9299e-03
     24052 -1.5903e-01
     24053 -1.8380e-02
     24054 -4.6613e-03
     25055 -9.9999e-03
     26054 -3.9616e-02
     26056 -6.4489e-01
     26057 -1.5160e-02
     26058 -2.0529e-03
     28058 -6.2157e-02
     28060 -2.4767e-02
     28061 -1.0946e-03
     28062 -3.5473e-03
     28064 -9.3243e-04
C name: Boral (65% Al-35% B4C)
C density = 2.5
m4
     5010 -5.0501e-02
     5011 -2.2350e-01
     6012 -7.5120e-02
     6013 -8.8041e-04
     13027 -6.5000e-01
m1
     1001 -1.1210e-01
     1002 -2.5766e-05
     8016 -8.8752e-01
     8017 -3.5930e-04
 mt1        lwtr.20t                                           $Thermal Treatment
m90000
     1001 -1.0010e-02
     1002 -2.3008e-06
     6012 -9.8962e-04
     6013 -1.1598e-05
     8016 -5.2832e-01
     8017 -2.1388e-04
     11023 -1.6020e-02
     12024 -1.5609e-03
     12025 -2.0585e-04
     12026 -2.3569e-04
     13027 -3.3913e-02
     14028 -3.0999e-01
     14029 -1.6310e-02
     14030 -1.1135e-02
     19039 -1.2097e-02
     19040 -1.5566e-06
     19041 -9.1775e-04
     20040 -4.2583e-02
     20042 -2.9840e-04
     20043 -6.3747e-05
     20044 -1.0079e-03
     20046 -2.0205e-06
     20048 -9.8567e-05
     26054 -7.9134e-04
     26056 -1.2882e-02
     26057 -3.0282e-04
     26058 -4.1006e-05
C name: Boron Carbide
C density = 2.5
m3
     5010 -1.4424e-01
     5011 -6.3837e-01
     6012 -2.1487e-01
     6013 -2.5183e-03
c
c    Fuel Data                     
m10000000
     1001 -7.4958e-03
     1002 -1.7229e-06
     6012 -1.6247e-05
     6013 -1.9042e-07
     8016 -1.6486e-01
     8017 -6.6741e-05
     14028 -1.8876e-04
     14029 -9.9318e-06
     14030 -6.7804e-06
     15031 -9.4518e-06
     16032 -5.8384e-06
     16033 -4.7539e-08
     16034 -2.7753e-07
     16036 -6.9144e-10
     24050 -3.2588e-04
     24052 -6.5352e-03
     24053 -7.5531e-04
     24054 -1.9156e-04
     25055 -4.1095e-04
     26054 -1.6280e-03
     26056 -2.6502e-02
     26057 -6.2299e-04
     26058 -8.4362e-05
     28058 -2.5544e-03
     28060 -1.0178e-03
     28061 -4.4982e-05
     28062 -1.4578e-04
     28064 -3.8318e-05
     92235 -4.7189e-02
     92238 -7.3929e-01
m50000000
     1001 -7.4958e-03
     1002 -1.7229e-06
     6012 -1.6247e-05
     6013 -1.9042e-07
     8016 -1.6486e-01
     8017 -6.6741e-05
     14028 -1.8876e-04
     14029 -9.9318e-06
     14030 -6.7804e-06
     15031 -9.4518e-06
     16032 -5.8384e-06
     16033 -4.7539e-08
     16034 -2.7753e-07
     16036 -6.9144e-10
     24050 -3.2588e-04
     24052 -6.5352e-03
     24053 -7.5531e-04
     24054 -1.9156e-04
     25055 -4.1095e-04
     26054 -1.6280e-03
     26056 -2.6502e-02
     26057 -6.2299e-04
     26058 -8.4362e-05
     28058 -2.5544e-03
     28060 -1.0178e-03
     28061 -4.4982e-05
     28062 -1.4578e-04
     28064 -3.8318e-05
     92235 -4.7189e-02
     92238 -7.3929e-01
c
c
c  DATA
c    kcode              
kcode 5000 1 15 25 
ksrc 0 0 0
         0 -250 0
        -150 0 -100
        150 0 0
        0 150 0
        -150 0 0
        0 -150 0
        150 0 100
        0 150 100
        0 0 100
        -150 0 100
c                       
mode n
print
c
c  ------------------------------  End of file  -----------------------------  c
