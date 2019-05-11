from flask import Flask, render_template, request, redirect
from flaskext.mysql import MySQL
import boto3

app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'huck12554557796539'
app.config['MYSQL_DATABASE_DB'] = 'promocodes'
app.config['MYSQL_DATABASE_HOST'] = 'mishajulyafil.cmqxvioimslz.eu-west-1.rds.amazonaws.com'

mysql.init_app(app)

@app.route('/', methods=['POST','GET'])
def hello():

    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():

    userDetails = request.form
    store = userDetails['store']
    site = userDetails['site']
    good = userDetails['good']
    
    description = userDetails['description']
    promocode = userDetails['promocode']
    start = userDetails['stdate']
    end = userDetails['edate']
    cur = mysql.get_db().cursor()
    cur.execute("INSERT INTO stores(name, site) VALUES(%s, %s);",(store, site))
    mysql.get_db().commit()
    cur.execute("SELECT MAX(id) FROM stores")
    insert_id = cur.fetchone()[0]
    
    image = 'https://s3-eu-west-1.amazonaws.com/elasticbeanstalk-eu-west-1-001336487002/'+str(insert_id)

    cur.execute("INSERT INTO goods(name,image,description) VALUES (%s, %s, %s);",(good, image, description))
    mysql.get_db().commit()
    cur.execute("INSERT INTO coupons (storesID,goodsID,promocode,start,end) VALUES (%s,%s,%s,%s,%s);",(insert_id,insert_id,promocode,start,end))
    mysql.get_db().commit()
    cur.close()
    s3 = boto3.resource('s3')
    s3.Bucket('elasticbeanstalk-eu-west-1-001336487002').put_object(Key=str(insert_id), Body=request.files['image'])

    return redirect('/users')
 
@app.route('/users')
def users():
    cur = mysql.get_db().cursor()
    resultValue = cur.execute(
"SELECT promocode,goods.description,goods.name,image,site,start,end FROM coupons,goods,stores WHERE storesID=stores.id AND goodsID=goods.id"
)
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('users.html',userDetails=userDetails)
