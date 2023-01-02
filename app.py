from flask import Flask,render_template,url_for,request,redirect,session,make_response,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate
from datetime import date,timedelta
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os,requests,io
from imagekitio import ImageKit

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db,render_as_batch=True)

imagekit = ImageKit(private_key=app.config['PRIKEYIMGKIT'],
                    public_key=app.config['PUBKEYIMGKIT'],
                    url_endpoint = app.config['URLENDIMGKIT'])

class tbluser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    aplikasi = db.Column(db.String(64))
    valid = db.Column(db.String(64))
    # last_name = db.Column(db.String(64))

class tbljanjian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    realnamaproduk = db.Column(db.String(175))
    realsku = db.Column(db.String(64))
    plnfi = db.Column(db.Integer)
    hargajanjian = db.Column(db.Integer)
    startdate = db.Column(db.Date)
    enddate = db.Column(db.Date)
    notes=db.Column(db.Text)

class tblkonten(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64))
    herourl = db.Column(db.String(64))
    prod_desc = db.Column(db.Text)


@app.route('/<mp>',methods=['POST','GET'])
def index(mp):
    print(mp)
    session['mp']=mp
    print (session.get('mp', 'not set'))
    # df=tbluser.query.all()
    # print(df)
    # if request.method=='POST':
    #     newuser=tbluser(first_name=request.form['fname'],last_name=request.form['lname'])
    #     db.session.add(newuser)
    #     db.session.commit()
    #     return redirect(url_for('index'))
    return render_template('home2.html')

@app.route('/allcustdb',methods=['POST','GET'])
def allcustdb():
    df=tbluser.query.all()
    return render_template('allcust.html',df=df)

@app.route('/delete<id>',methods=['POST','GET'])
def delete(id):
    deluser=tbluser.query.get(id)
    db.session.delete(deluser)
    db.session.commit()
    return redirect(url_for('allcustdb'))

@app.route('/form',methods=['POST','GET'])
def form():
    print (session.get('mp', 'not set'))
    if request.method=='POST':
        newuser=tbluser(first_name=request.form['qnama'],email=request.form['qemail'],phone=request.form['qphone'],aplikasi=request.form['q1'],valid=request.form['q6'])
        db.session.add(newuser)
        db.session.commit()
        return redirect(url_for('form2'))
    return render_template('form.html')

@app.route('/janjianharga',methods=['POST','GET'])
def janjianharga():
    item_name=request.args.get('item_name')
    item_sku=request.args.get('item_sku')
    item_pl=request.args.get('item_pl')
    cnx = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    df=pd.read_sql(f"SELECT * FROM tbljanjian WHERE realsku = '{item_sku}'", con=cnx)
    cnx.dispose()
    if request.method=='POST':
        cek_a=df[(df['enddate']>request.form['jh_startdate'])&(df['startdate']<request.form['jh_enddate'])]['id']
        cek_c=df[(df['startdate']<request.form['jh_startdate'])&(df['enddate']>request.form['jh_enddate'])]['id']
        cek_d=df[(df['startdate']>request.form['jh_startdate'])&(df['enddate']<request.form['jh_enddate'])]['id']
        cek=cek_a.append(cek_c).append(cek_d)
        print (len(cek))
        if request.form['jh_startdate'] < request.form['jh_enddate']:
            if len(cek)==0:
                y1=int(request.form['jh_startdate'].split('-')[0])
                m1=int(request.form['jh_startdate'].split('-')[1])
                d1=int(request.form['jh_startdate'].split('-')[2])
                y2=int(request.form['jh_enddate'].split('-')[0])
                m2=int(request.form['jh_enddate'].split('-')[1])
                d2=int(request.form['jh_enddate'].split('-')[2])
                newjanjian=tbljanjian(realnamaproduk=request.form['jh_itemname'],realsku=request.form['jh_itemsku'],plnfi=request.form['jh_plnfi'],hargajanjian=request.form['jh_harga'],startdate=date(year=y1,month=m1,day=d1),enddate=date(year=y2,month=m2,day=d2),notes=request.form['jh_notes'])
                db.session.add(newjanjian)
                db.session.commit()
                return redirect(url_for('listjanjianharga'))
            else:
                return render_template('janjianharga.html',a=item_name,b=item_sku,c=item_pl,msg="overlap promo plan",df=df[['startdate','enddate','hargajanjian','notes']].rename(columns={'startdate':'Start Date','enddate':'End Date','hargajanjian':'Harga Janjian'}).to_html(index=False,classes='table table-striped table-hover'))


        else:
            return render_template('janjianharga.html',a=item_name,b=item_sku,c=item_pl,msg="start date must be less than end date",df=df[['startdate','enddate','hargajanjian','notes']].rename(columns={'startdate':'Start Date','enddate':'End Date','hargajanjian':'Harga Janjian'}).to_html(index=False,classes='table table-striped table-hover'))
    return render_template('janjianharga.html',a=item_name,b=item_sku,c=item_pl,df=df[['startdate','enddate','hargajanjian','notes']].rename(columns={'startdate':'Start Date','enddate':'End Date','hargajanjian':'Harga Janjian'}).to_html(index=False,classes='table table-striped table-hover'))

@app.route('/listjanjianharga',methods=['POST','GET'])
def listjanjianharga():
    msg=tbljanjian.query.filter(tbljanjian.enddate<=date.today()+timedelta(days=7),tbljanjian.enddate>date.today(),tbljanjian.startdate<=date.today()).count()
    df_active=tbljanjian.query.filter(tbljanjian.enddate>date.today(),tbljanjian.startdate<=date.today()).all()
    df_pending=tbljanjian.query.filter(tbljanjian.startdate>date.today()).all()
    df_selesai=tbljanjian.query.filter(tbljanjian.enddate<date.today()).all()
    return render_template('listjanjian.html',df=df_active,df2=df_pending,msg=msg,df_selesai=df_selesai)

@app.route('/deljanjian/<id>',methods=['POST','GET'])
def deljanjian(id):
    if request.method=='POST':
        deljanji=tbljanjian.query.get(id)
        db.session.delete(deljanji)
        db.session.commit()
        return redirect(url_for('listjanjianharga'))
    else:
        return render_template('delconfirm.html',id=id)

@app.route('/editjanjian/<id>',methods=['GET','POST'])
def editjanjian(id):
    itemjanjian=tbljanjian.query.get(id)
    cnx = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    df=pd.read_sql(f"SELECT * FROM tbljanjian WHERE realsku = '{itemjanjian.realsku}'", con=cnx)
    df['id']=df['id'].astype(str)
    df['enddate']=pd.to_datetime(df["enddate"], format="%Y/%m/%d")
    df['startdate']=pd.to_datetime(df["startdate"], format="%Y/%m/%d")
    print(df)
    cnx.dispose()
    if request.method == 'GET':
        return render_template('editjanjian.html',item=itemjanjian)
    else:
        cek_a=df[(df['enddate']>request.form['jh_startdate'])&(df['startdate']<request.form['jh_enddate'])&(df['id']!=str(id))]['id']
        cek_c=df[(df['startdate']<request.form['jh_startdate'])&(df['enddate']>request.form['jh_enddate'])&(df['id']!=str(id))]['id']
        cek_d=df[(df['startdate']>request.form['jh_startdate'])&(df['enddate']<request.form['jh_enddate'])&(df['id']!=str(id))]['id']
        cek=cek_a.append(cek_c).append(cek_d)
        # print(df[id].info())
        if request.form['jh_startdate'] < request.form['jh_enddate']:
            if len(cek)==0:
                y1=int(request.form['jh_startdate'].split('-')[0])
                m1=int(request.form['jh_startdate'].split('-')[1])
                d1=int(request.form['jh_startdate'].split('-')[2])
                y2=int(request.form['jh_enddate'].split('-')[0])
                m2=int(request.form['jh_enddate'].split('-')[1])
                d2=int(request.form['jh_enddate'].split('-')[2])
                # newjanjian=tbljanjian(realnamaproduk=request.form['jh_itemname'],realsku=request.form['jh_itemsku'],plnfi=request.form['jh_plnfi'],hargajanjian=request.form['jh_harga'],startdate=date(year=y1,month=m1,day=d1),enddate=date(year=y2,month=m2,day=d2),notes=request.form['jh_notes'])
                itemjanjian.hargajanjian=request.form['jh_harga']
                itemjanjian.startdate=date(year=y1,month=m1,day=d1)
                itemjanjian.enddate=date(year=y2,month=m2,day=d2)
                db.session.add(itemjanjian)
                db.session.commit()
                return redirect(url_for('listjanjianharga'))
            else:
                return render_template('editjanjian.html',item=itemjanjian,msg="overlap promo plan")
        else:
            return render_template('editjanjian.html',item=itemjanjian,msg="start date must be less than end date")

@app.route('/download/<type>',methods=['GET', 'POST'])
def download(type):
    cnx = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    if type=='janjianharga':
        df=pd.read_sql_table('tbljanjian', con=cnx)
    else:
        df=pd.read_sql_table('tbluser', con=cnx)
    cnx.dispose()

    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')
    df.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
    writer.save()
    writer.close()
    resp = make_response(out.getvalue())
    resp.headers["Content-Disposition"] = f"attachment; filename=export_{type}.xlsx"
    resp.headers["Content-type"] = "application/x-xls"

    # resp = make_response(df.to_csv(index=False))
    # resp.headers["Content-Disposition"] = f"attachment; filename=export_{type}.csv"
    # resp.headers["Content-Type"] = "text/csv"
    return resp

@app.route('/form2',methods=['POST','GET'])
def form2():
    return render_template('form2.html')

@app.route('/reward',methods=['POST','GET'])
def reward():
    return render_template('reward.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['ppfile']
        ppdate = request.form['ppdate']
        btl_ts_s = int(request.form['btl_s_ts'])
        btl_ts_b = int(request.form['btl_b_ts'])
        btl_hilo_s = int(request.form['btl_s_hilo'])
        btl_hilo_b = int(request.form['btl_b_hilo'])
        btl_lmen_s = int(request.form['btl_s_lmen'])
        btl_lmen_b = int(request.form['btl_b_lmen'])
        btl_wdank_s = int(request.form['btl_s_wdank'])
        btl_wdank_b = int(request.form['btl_b_wdank'])
        btl_ns_s = int(request.form['btl_s_ns'])
        btl_ns_b = int(request.form['btl_b_ns'])

        print(ppdate)
        filedir=os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
        cnx = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        if ".xlsx" in filedir:
            #### read upload file    
            f.save(filedir)          
            df=pd.read_excel(filedir,engine='openpyxl')
            
            #### download from tatanama
            data_sku=requests.get('https://tatanama.pythonanywhere.com/apinew')
            data_sku=pd.DataFrame(data_sku.json())
            data_sku=data_sku[['SKU','Brand','Nama_Produk','Harga_Display','Price_List_NFI',
                                'SKU_Produk_1','PCS_Produk_1','Price_List_NFI_1',
                                'SKU_Produk_2','PCS_Produk_2','Price_List_NFI_2',
                                'SKU_Produk_3','PCS_Produk_3','Price_List_NFI_3',
                                'SKU_Produk_4','PCS_Produk_4','Price_List_NFI_4',
                                'SKU_Produk_5','PCS_Produk_5','Price_List_NFI_5',
                                'SKU_Produk_6','PCS_Produk_6','Price_List_NFI_6',
                                'SKU_Produk_7','PCS_Produk_7','Price_List_NFI_7']] 
            colint=[x for x in data_sku.columns if not 'SKU' in x and not 'Nama' in x and not 'Brand' in x]
            data_sku[colint] = data_sku[colint].apply(pd.to_numeric, errors='coerce')
            data_sku=data_sku[data_sku['SKU'].isin(df['SKU'].astype(str).unique())]
            skuNs=data_sku[data_sku['Brand']=='NS']['SKU'].unique()
            skuTs=data_sku[data_sku['Brand']=='TS']['SKU'].unique()
            skuHl=data_sku[data_sku['Brand']=='HiLo']['SKU'].unique()
            skuLm=data_sku[data_sku['Brand']=='L-Men']['SKU'].unique()
            skuWd=data_sku[data_sku['Brand']=="W'dank"]['SKU'].unique()
            # skuNs=data_sku[data_sku['Brand']=='NS']['SKU'].unique()
            
            #### data cleaning for tatanama
            for i in [1,2,3,4,5,6,7]:
                data_sku.loc[data_sku[f'Price_List_NFI_{i}'].isin([0,'',None]),f'Price_List_NFI_{i}']=np.nan
                data_sku.loc[data_sku[f'Price_List_NFI_{i}'].isnull(),f'Price_List_NFI_{i}']=np.nan
                data_sku.loc[data_sku[f'PCS_Produk_{i}'].isin([0,'',None]),f'PCS_Produk_{i}']=np.nan
                data_sku.loc[data_sku[f'PCS_Produk_{i}'].isnull(),f'PCS_Produk_{i}']=np.nan
                data_sku.loc[data_sku[f'SKU_Produk_{i}'].isin([0,'',None]),f'SKU_Produk_{i}']=np.nan
                data_sku.loc[data_sku[f'SKU_Produk_{i}'].isnull(),f'SKU_Produk_{i}']=np.nan
            
            #### subtotal for non janjian bundle
            for i in [1,2,3,4,5,6,7]:
                data_sku[f'subtotal_pl_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']
                data_sku[f'subtotal_tier1_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']*1
                data_sku.loc[data_sku[f'SKU_Produk_{i}'].isin(skuNs),f'subtotal_tier1_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']*(100-btl_ns_b)/100
                data_sku.loc[data_sku[f'SKU_Produk_{i}'].isin(skuTs),f'subtotal_tier1_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']*(100-btl_ts_b)/100
                data_sku.loc[data_sku[f'SKU_Produk_{i}'].isin(skuHl),f'subtotal_tier1_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']*(100-btl_hilo_b)/100
                data_sku.loc[data_sku[f'SKU_Produk_{i}'].isin(skuLm),f'subtotal_tier1_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']*(100-btl_lmen_b)/100
                data_sku.loc[data_sku[f'SKU_Produk_{i}'].isin(skuWd),f'subtotal_tier1_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']*(100-btl_wdank_b)/100
                # data_sku.loc[data_sku[f'SKU_Produk_{i}'].isin(skuNs),f'subtotal_tier1_{i}']=data_sku[f'PCS_Produk_{i}']*data_sku[f'Price_List_NFI_{i}']*1.04
            
            #### read data janjian active
            janjian=pd.read_sql_table('tbljanjian', con=cnx)
            cnx.dispose()
            janjian=janjian[(janjian['startdate']<=ppdate)&(janjian['enddate']>=ppdate)]
            janjian['realsku']=janjian['realsku'].astype(str)
            janjian=janjian[['realsku','hargajanjian']].rename(columns={'realsku':'SKU'})
            data_sku=data_sku.merge(janjian,how='left')
            for i in [1,2,3,4,5,6,7]:
                janjian_m=janjian.rename(columns={'SKU':f'SKU_Produk_{i}','hargajanjian':f'hargajanjian{i}'})
                data_sku=data_sku.merge(janjian_m,how='left')
            data_sku_copy=data_sku.fillna(0).copy()

            #### subtotal for bundle with harga janjian
            for i in [1,2,3,4,5,6,7]:
                data_sku_copy.loc[data_sku_copy[f'hargajanjian{i}']!=0,f'subtotal_tier1_{i}']=data_sku_copy[f'PCS_Produk_{i}']*(data_sku_copy[f'hargajanjian{i}']-500)
            
            #### pricing for bundle
            data_sku_copy['Pricing Tier 1']=data_sku_copy['subtotal_tier1_1']+data_sku_copy['subtotal_tier1_2']+data_sku_copy['subtotal_tier1_3']+data_sku_copy['subtotal_tier1_4']+data_sku_copy['subtotal_tier1_5']+data_sku_copy['subtotal_tier1_6']+data_sku_copy['subtotal_tier1_7']
            data_sku_copy['Pricing Tier 1']=round(data_sku_copy['Pricing Tier 1'],-2)

            #### pricing for single item janjian
            data_sku_copy.loc[data_sku_copy['Pricing Tier 1']==0,'Pricing Tier 1']=data_sku_copy['hargajanjian']
            # data_sku_copy.loc[(data_sku_copy['Pricing Tier 1']==0)&(data_sku_copy['Brand']=='NS'),'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*1.05,-2)
            
            #### pricing for non janjian single
            
            data_sku_copy.loc[(data_sku_copy['Pricing Tier 1']==0)&(data_sku_copy['Brand']=='NS'),'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*(100-btl_ns_s)/100,-2)
            data_sku_copy.loc[(data_sku_copy['Pricing Tier 1']==0)&(data_sku_copy['Brand']=='TS'),'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*(100-btl_ts_s)/100,-2)
            data_sku_copy.loc[(data_sku_copy['Pricing Tier 1']==0)&(data_sku_copy['Brand']=='HiLo'),'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*(100-btl_hilo_s)/100,-2)
            data_sku_copy.loc[(data_sku_copy['Pricing Tier 1']==0)&(data_sku_copy['Brand']=='L-Men'),'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*(100-btl_lmen_s)/100,-2)
            data_sku_copy.loc[(data_sku_copy['Pricing Tier 1']==0)&(data_sku_copy['Brand']=="W'dank"),'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*(100-btl_ns_s)/100,-2)
            data_sku_copy.loc[data_sku_copy['Pricing Tier 1']==0,'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*1,-2)
            # data_sku_copy.loc[(data_sku_copy['Pricing Tier 1']==0)&(data_sku_copy['Brand']=='NS'),'Pricing Tier 1']=round(data_sku_copy['Price_List_NFI']*0.98,-2)

            
            #### pricing for janjian bundle
            data_sku_copy.loc[data_sku_copy['hargajanjian']!=0,'Pricing Tier 1']=data_sku_copy['hargajanjian']
            data_sku_copy=data_sku_copy[['SKU','Nama_Produk','Harga_Display','Price_List_NFI','Pricing Tier 1']]

            out = io.BytesIO()
            writer = pd.ExcelWriter(out, engine='xlsxwriter')
            data_sku_copy.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
            writer.save()
            writer.close()
            resp = make_response(out.getvalue())
            resp.headers["Content-Disposition"] = f"attachment; filename=export_promoplan.xlsx"
            resp.headers["Content-type"] = "application/x-xls"

            # resp = make_response(data_sku_copy.to_csv(index=False))
            # resp.headers["Content-Disposition"] = f"attachment; filename=export_promoplan.csv"
            # resp.headers["Content-Type"] = "text/csv"
            return resp
        else:
            return render_template('upload.html',msg="FILE ERROR")
    else:
        return render_template('upload.html')

@app.route("/downtemp", methods=['GET', 'POST'])
def downtemp():
    return send_file('static/generate promoplan template.xlsx')

@app.route("/konten", methods=['GET', 'POST'])
def konten():
    if request.method == 'POST':
        print('masuk')
        f=request.files['hifile']
        filedir=os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
        # filedir=f"http://nutrimartevent.pythonanywhere.com/{filedir}"
        filedir="http://nutrimartevent.pythonanywhere.com/static/upload/android-chrome-192x192_1.png"
        upload = imagekit.upload_file(file=filedir,file_name="test-url.jpg")
        print(upload)
        res=upload.response_metadata.raw
        return render_template('konten.html',res=res)
    else:
        return render_template('konten.html')

@app.route('/proddesc/<sku>',methods=['POST','GET'])
def proddesc(sku):
    df=tblkonten.query.filter_by(sku=sku).first()
    if request.method == 'POST':
        if df:
            f=request.files['formHero']
            if f:
                print('ada file')
                ftype=f.content_type.split('/')[1]
                if ftype in ['jpeg','jpg','png']:
                    f.filename = f"{sku}_h.{ftype}"
                    filedir=os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
                    f.save(filedir)
                    df.herourl=filedir              
                else:
                    return render_template('wysiwyg.html',df=df,sku=sku,msg="not image")
            # else:
            df.prod_desc=request.form['editordata']
            db.session.add(df)
            db.session.commit()
            return redirect(url_for("proddesc",sku=sku))
        else:
            print('ok')
            f=request.files['formHero']
            ftype=f.content_type.split('/')[1]
            if ftype in ['jpeg','jpg','png']:
                f.filename = f"{sku}_h.{ftype}"
                filedir=os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
                f.save(filedir)
                newdata=tblkonten(herourl=filedir,prod_desc=request.form['editordata'],sku=sku)
                db.session.add(newdata)
                db.session.commit()
                return redirect(url_for("proddesc",sku=sku))
            else:
                return render_template('wysiwyg.html',df=df,sku=sku,msg="not image")
    else:
        return render_template('wysiwyg.html',df=df,sku=sku)

@app.route('/delproddesc/<id>',methods=['POST','GET'])
def delproddesc(id):
    deldata=tblkonten.query.get(id)
    db.session.delete(deldata)
    db.session.commit()
    return redirect(url_for("proddesclist"))

@app.route('/proddesclist',methods=['POST','GET'])
def proddesclist():
    df=tblkonten.query.all()
    return render_template('proddesc.html',df=df)

if __name__ == '__main__':
    app.run()
