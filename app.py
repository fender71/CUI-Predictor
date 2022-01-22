#import libraries
from flask import Flask, render_template,request
import pickle#Initialize the flask App
app = Flask(__name__)
model = pickle.load(open('Python/model.pkl', 'rb'))

#default page of our web-app
@app.route('/')
def home():
    return render_template('index.html')

    #To use the predict button in our web-app
@app.route('/predict',methods=['POST'])
def predict():
    #For rendering results on HTML GUI
    Pipe_Size = request.form.get("Pipe_Size")
    Pipe_Component = request.form.get("Component")
    Coating_Age = request.form.get("Coating_Age")
    Insulation= request.form.get("Insulation")
    Avg_Temp= request.form.get("Avg_Temp")
    Min_Temp= request.form.get("Min_Temp")
    Max_Temp= request.form.get("Max_Temp")
    Elevation= request.form.get("Elevation")
    Distance_X= request.form.get("Distance_X")
    Distance_Y= request.form.get("Distance_Y")
    Jacket_Condition = request.form.get("Jacket_Condition")
    Sealing_Condition = request.form.get("Sealing_Condition")
    Damage_Area = request.form.get("Damage_Area")

    #Convert Temp
    Avg_Temp = ((float(Avg_Temp)-32)*5)/9
    Min_Temp = ((float(Min_Temp)-32)*5)/9
    Max_Temp = ((float(Max_Temp)-32)*5)/9

    Range_Temp = float(Max_Temp)-float(Min_Temp)

    #Theoretical Corrosion Rate
    if float(Avg_Temp) < -12.0:
        Based_Corrosion_Rate = 0
    elif float(Avg_Temp) >= -12.0 and float(Avg_Temp) < -8.0:
        Based_Corrosion_Rate = 0.025
    elif float(Avg_Temp) >= -8.0 and  float(Avg_Temp) < 6.0:
        Based_Corrosion_Rate = 0.127
    elif  float(Avg_Temp) >= 6.0 and  float(Avg_Temp) < 32.0:
        Based_Corrosion_Rate = 0.127   
    elif  float(Avg_Temp) >= 32.0 and  float(Avg_Temp) < 71.0:
        Based_Corrosion_Rate = 0.254
    elif  float(Avg_Temp) >= 71.0 and  float(Avg_Temp) < 107.0:
        Based_Corrosion_Rate = 0.254
    elif  float(Avg_Temp) >= 107.0 and  float(Avg_Temp) < 135.0:
        Based_Corrosion_Rate = 0.127 
    elif  float(Avg_Temp) >= 135.0 and  float(Avg_Temp) < 162.0:
        Based_Corrosion_Rate = 0.051
    elif  float(Avg_Temp) >= 162.0 and  float(Avg_Temp) < 176.0:
        Based_Corrosion_Rate = 0.025        
    elif  float(Avg_Temp) >= 176.0:
        Based_Corrosion_Rate = 0   

    if Insulation == 'Foam Glass':
        Insulation_Factor = 0.75
    elif Insulation == 'Mineral Wool' or Insulation == 'Calcium Silicate':
        Insulation_Factor = 1.25                
    else:
        Insulation_Factor = 1.25

    if Pipe_Component == 'Pipe/Elbow':
        Complexity_Factor = 1           
    else:
        Complexity_Factor = 1.25

    if Damage_Area == "No Damage":
        Condition_Factor = 0.75          
    elif Damage_Area =="High":
        Condition_Factor = 1.25    
    elif Damage_Area == "Medium":
        Condition_Factor = 1.12    
    elif Damage_Area == "Low":
        Condition_Factor = 1.0  

    Theoretical_Corrosion_Rate = 2*Based_Corrosion_Rate*Insulation_Factor*Complexity_Factor*Condition_Factor
    Theoretical_Corrosion_Rate = round(Theoretical_Corrosion_Rate,4)

    #CUI Risk Score
    if float(Avg_Temp) >= -4 and float(Avg_Temp) <= 38:
        Temp_Score = 1   
    elif float(Avg_Temp) >= 132 and float(Avg_Temp) <= 177:
        if Range_Temp >= 93:   #Cyclic
            Temp_Score = 5
        else:
            Temp_Score = 1     
            
    elif float(Avg_Temp) >= 38 and float(Avg_Temp) <= 77:
        Temp_Score = 3     
    elif float(Avg_Temp) >= 110 and float(Avg_Temp) <= 132:
        if Range_Temp >= 93:   #Cyclic
            Temp_Score = 5
        else:
            Temp_Score = 3
            
    elif float(Avg_Temp) >= 77 and float(Avg_Temp) <= 100:
        Temp_Score = 5             
    else:
        Temp_Score = 0

    if float(Coating_Age) < 8 :
        Age_Score = 0 
    elif float(Coating_Age) >= 8 and float(Coating_Age) <= 15:
        Age_Score = 3
    elif float(Coating_Age) > 15:
        Age_Score = 5


    if Damage_Area == "No Damage" :
        Condition_Score = 1
    elif Damage_Area == "Low":
        Condition_Score = 3
    else:
        Condition_Score = 5

    if Insulation== 'Foam Glass':
        Insulation_Score = 1
    else: 
        Insulation_Score = 5  

    if float(Pipe_Size) > 6 :
        Size_Score = 1    
    elif float(Pipe_Size) >= 2 and float(Pipe_Size) <= 6:
        Size_Score = 3   
    elif float(Pipe_Size) < 2:
        Size_Score = 5  

    CUI_Risk_Score = Temp_Score+Age_Score+Condition_Score+0+5+Insulation_Score+Size_Score
    CUI_Risk_Score = round(CUI_Risk_Score,4)

    #data_input
    data_input = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    data_input[0][0] = float(Avg_Temp)
    data_input[0][1] = float(Range_Temp)
    data_input[0][2] = float(Coating_Age)
    data_input[0][3] = float(Pipe_Size)

    if Jacket_Condition == "Good":
        data_input[0][4] = 0
    elif Jacket_Condition == "Damage":
        data_input[0][4] = 1

    if Sealing_Condition == "Good":
        data_input[0][5] = 0
    elif Sealing_Condition == "Damage":
        data_input[0][5] = 1

    if Damage_Area == "No Damage":
        data_input[0][6] = 0
    elif Damage_Area =="High":
        data_input[0][6] = 3 
    elif Damage_Area == "Medium":
        data_input[0][6] = 2
    elif Damage_Area == "Low":
        data_input[0][6] = 1

    data_input[0][7] = float(Elevation)
    data_input[0][8] = float(Distance_X)
    data_input[0][9] = float(Distance_Y)
    data_input[0][10] = CUI_Risk_Score
    data_input[0][11] = Theoretical_Corrosion_Rate

    if Insulation == "Calcium Silicate":
        data_input[0][13] = 1
    elif Insulation == "Foam Glass":
        data_input[0][14] = 1 
    elif Insulation == "Mineral Wool":
        data_input[0][15] = 1
    else:
        data_input[0][12] = 1

    if Pipe_Component== "Pipe/Elbow":
        data_input[0][16] = 1
    elif Pipe_Component == "Tee/Valve":
        data_input[0][17] = 1 

    prediction = model.predict(data_input)

    if prediction == ['0_No_Corrosion']:
        prediction = "No_Corrosion"

    elif prediction == ['1_Slight_Corrosion']:
        prediction = "Slight_Corrosion"

    elif prediction == ['2_Significant_Corrosion']:
        prediction = "Significant_Corrosion"


    #Convert Temp Back for report
    Avg_Temp = ((9*Avg_Temp)/5)+32 
    Min_Temp = ((9*Min_Temp)/5)+32 
    Max_Temp = ((9*Max_Temp)/5)+32 



    return render_template('index.html', 
    prediction_text='Predicted CUI Severity is : {}'.format(prediction),
    pipe_size_text='Pipe Size : {}'.format(Pipe_Size)+' inch',
    pipe_component_text='Pipe Component : {}'.format(Pipe_Component),
    coating_text='Coating Age : {}'.format(Coating_Age)+' year',
    insulation_text='Insulation Material : {}'.format(Insulation),
    avg_temp_text='Average Operating Temperature : {}'.format(Avg_Temp)+' degreeF',
    min_temp_text='Minimum Operating Temperature : {}'.format(Min_Temp)+' degreeF',
    max_temp_text='Maximum Operating Temperature : {}'.format(Max_Temp)+' degreeF',
    elevation_text='Elevation : {}'.format(Elevation)+' Feet',
    distx_text='Distance from Center in X_Axis (0=Center, 0.5=Edge) : {}'.format(Distance_X),
    disty_text='Distance from Center in Y_Axis (0=Center, 0.5=Edge) : {}'.format(Distance_Y),
    jacket_text='Jacket Condition : {}'.format(Jacket_Condition),
    sealing_text='Sealing Condition : {}'.format(Sealing_Condition),
    damage_text='Damage Area : {}'.format(Damage_Area),
    thcr_text='Theoretical_Corrosion_Rate per API 581 : {}'.format(Theoretical_Corrosion_Rate)+' mm per year',
    cui_risk_score_text='CUI Risk Score per API 583 : {}'.format(CUI_Risk_Score))


#    return render_template('index.html', pipe_text='Pipe Size : {}'.format(Pipe_Size)+' inch')

if __name__ == "__main__":
    app.run(debug=True)