from flask_sqlalchemy import SQLAlchemy
from flask import Flask,request, render_template, redirect,url_for, session
from model import db, Customer, Professional, Admin, Service, ServiceRequest
from app import db
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
from users import getUserInfo, getAllServices, getAllProfessional, getServiceInfo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.secret_key = 'supersecretkey' 
db.init_app(app) 
app.app_context().push()
db.create_all()

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/login', methods=['GET','POST'])
def login():
    eemail=request.form.get('email')
    ppassword=request.form.get('password')
    iuser = Customer.query.filter_by(email=eemail).first() 
    suser = Professional.query.filter_by(email=eemail).first()
    auser = Admin.query.filter_by(email=eemail).first()
    if iuser and iuser.password==ppassword:
        session['id']=iuser.id
        session['eemail']=iuser.email
        return redirect(url_for('home'))
    elif suser and suser.password==ppassword:
        session['id']=suser.id
        session['eemail']=suser.email
        if suser.status == 'pending':
            return redirect(url_for('pending'))
        elif suser.status == 'rejected':
            return redirect(url_for('rejected'))
        return redirect(url_for('home'))
    elif auser and auser.password == ppassword:
        session['id']=auser.id
        session['eemail']=auser.email
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/pending')
def pending():
    return render_template('pending.html')

@app.route('/rejected')
def rejected():
    return render_template('rejected.html')

@app.route('/home')
def home():
    user_info=getUserInfo()
    return render_template('home.html',user=user_info)

@app.route('/customer',methods=['GET','POST'])
def customer():
    if request.method == 'POST':
        name=request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        pincode=request.form.get('pincode')
        if not name or not email or not password:
            return redirect(url_for('customer'))
        elif Customer.query.filter_by(email=email).first():
            return redirect(url_for('customer'))
        else:
            new_login= Customer(name=name,email=email,password=password,address=address,pincode=pincode)
            db.session.add(new_login)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('customer.html')  

@app.route('/professional',methods=['GET','POST'])
def professional():
    if request.method == 'POST':
        name=request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        service = request.form.get('service')
        address = request.form.get('address')
        experience = request.form.get('experience')
        pincode=request.form.get('pincode') 
        if not name or not email or not password:
            return redirect(url_for('professional'))
        elif Professional.query.filter_by(email=email).first():
            return redirect(url_for('professional'))
        else:
            new_login= Professional(name=name,email=email,password=password,address=address,pincode=pincode, service=service,experience=experience )
            db.session.add(new_login)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('professional.html')

@app.route('/custhome')
def custname():
    return render_template('custhome.html')

@app.route('/adminhome')
def adminhome():
    services = getAllServices()  
    professionals = getAllProfessional()
    results= ServiceRequest.query.all()
    service_req = db.session.query(
            ServiceRequest.id,
            ServiceRequest.service_id,
            ServiceRequest.customer_id,
            ServiceRequest.professional_id,
            Professional.name.label('professional_name'),
            ServiceRequest.date_of_request,
            ServiceRequest.service_status,
            ServiceRequest.remark
        ).join(Professional, ServiceRequest.professional_id == Professional.id)
    return render_template('adminhome.html', services=services, professionals=professionals, service_req = service_req,results=results )

@app.route('/serviceform',methods=['GET','POST'])
def serviceform():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        name=request.form.get('name')
        price=request.form.get('price')
        description=request.form.get('description')
        time=request.form.get('time')
        if not name or not price or not description:
            return redirect(url_for('serviceform'))
        elif Service.query.filter_by(name=name).first():
            return redirect(url_for('serviceform'))
        else:
            new_login= Service(name=name,price=price, description=description, time=current_time )
            db.session.add(new_login)
            db.session.commit()
            return redirect(url_for('adminhome'))
    return render_template('serviceform.html')


@app.route('/delete_service/<int:service_id>',methods=['POST'])
def delete_service(service_id):
    service=Service.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
    return redirect(url_for('adminhome'))

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get(service_id)
    if not service:
        return redirect(url_for('service_list')) 
    if request.method == 'POST':
        service.name = request.form.get('name')
        service.price = request.form.get('price')
        service.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('adminhome'))
    return render_template('edit_service.html', service=service)

@app.route('/custhome/<category>', methods=['GET', 'POST'])
def show_services(category):
    search_term = f"%{category}%"  
    services = Service.query.filter(Service.name.like(search_term)).all()
    print(services)
    if not services:
        return redirect(url_for('notfound'))
    return render_template('servicez.html', services=services, category=category)

@app.route('/notfound')
def notfound():
    return render_template('notfound.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    customer_id = session.get('id')  
    service_requests = db.session.query(ServiceRequest, Service, Professional).join(Service, ServiceRequest.service_id == Service.id).join(Professional, ServiceRequest.professional_id == Professional.id, isouter=True).filter(ServiceRequest.customer_id == customer_id).all()
    if request.method == 'POST':
        name = request.form.get('name')
        services = Service.query.filter(Service.name.ilike(f'%{name}%')).all()
        return render_template('search.html', services=services, service_requests=service_requests)
    return render_template('search.html', services=[], service_requests=service_requests)

@app.route('/search_service')
def search_service():
    service_info = getServiceInfo()
    if service_info:
        return render_template('search_service.html', services=service_info)
    else:
        return render_template('search_service.html', services=None)
    
@app.route('/book_service', methods=['POST'])
def book_service():
    service_id = request.form.get('service_id')
    customer_id = session.get('id')
    new_request = ServiceRequest(
        service_id=service_id,
        customer_id=customer_id,
        professional_id=None,
        date_of_request=date.today(),
        service_status='Requested'
    )
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('service_history'))

@app.route('/service_history')
def service_history():
    customer_id = session.get('id')
    service_requests = db.session.query(ServiceRequest, Service, Professional).join(Service, ServiceRequest.service_id == Service.id).join(Professional, ServiceRequest.professional_id == Professional.id, isouter=True).filter(ServiceRequest.customer_id == customer_id).all()
    return render_template('search.html', service_requests=service_requests)

@app.route('/admin/approve/<int:id>', methods=['POST'])
def approve_professional(id):
    professional = Professional.query.get(id)
    if professional:
        professional.status = 'approved'
        db.session.commit()
    return redirect(url_for('adminhome'))

@app.route('/admin/reject/<int:id>', methods=['POST'])
def reject_professional(id):
    professional = Professional.query.get(id)
    if professional:
        professional.status = 'rejected'
        db.session.commit()
    return redirect(url_for('adminhome'))

@app.route('/profhome', methods=['GET', 'POST'])
def profhome():
    professional = Professional.query.filter_by(id=session.get('id')).first()
    if request.method == 'POST':
        service_request_id = request.form.get('request_id')
        action = request.form.get('action')
        service_request = ServiceRequest.query.filter_by(id=service_request_id).first()
        if not service_request:
            print(f"No ServiceRequest found with ID: {service_request_id}")
            return redirect(url_for('profhome'))
        if action == 'accept':
            service_request.service_status = 'Accepted'
            service_request.professional_id = professional.id
            db.session.commit()
        elif action == 'reject':
            service_request.service_status = 'Rejected'
            db.session.commit()
        return redirect(url_for('profhome'))
    requests = db.session.query(
        ServiceRequest.id.label('request_id'),
        ServiceRequest.service_status,
        ServiceRequest.date_of_request,
        ServiceRequest.professional_id,
        Customer.name.label('customer_name'),
        Customer.address.label('customer_address'),
        Customer.pincode.label('customer_pincode')
    ).join(Customer, ServiceRequest.customer_id == Customer.id).filter(
        (ServiceRequest.professional_id == professional.id) |
        (ServiceRequest.professional_id == None)
    ).all()
    request_list = [
        {
            'request_id': r.request_id,
            'service_status': r.service_status,
            'date_of_request': r.date_of_request,
            'customer_name': r.customer_name,
            'customer_address': r.customer_address,
            'customer_pincode': r.customer_pincode
        } for r in requests
    ]
    return render_template('profhome.html', requests=request_list, professional=professional)

@app.route('/accept_service/<int:request_id>', methods=['POST'])
def accept_service(request_id):
    service_request = ServiceRequest.query.get(request_id)
    professional = Professional.query.filter_by(id=session.get('id')).first()
    if service_request and professional:
        service_request.service_status = 'Accepted'  
        service_request.professional_id = professional.id  
        db.session.commit()
    return redirect(url_for('profhome')) 

@app.route('/reject_service/<int:request_id>', methods=['POST'])
def reject_service(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        print(f"No ServiceRequest found with ID: {request_id}")
        return redirect(url_for('profhome'))
    service_request.service_status = 'Rejected'
    db.session.commit()
    return redirect(url_for('profhome'))

@app.route('/logout')
def logout():
    return render_template('login.html')

@app.route('/close_it/<int:request_id>', methods=['GET','POST'])
def close(request_id):
    if request.method == 'GET':
        return f"Page is working for request_id: {request_id}"
    service_rq = db.session.query(
    ServiceRequest.id,
    Service.name.label('service_name'),
    Professional.name.label('professional_name'),
    Professional.id.label('professional_id'),
    ServiceRequest.date_of_request
    ).join(Service, ServiceRequest.service_id == Service.id).join(Professional, ServiceRequest.professional_id == Professional.id).filter(ServiceRequest.id == request_id).first()
    if request.method == 'POST':
        date_of_completion = request.form.get('date_of_completion')
        remarks = request.form.get('remarks')
        service_rq_ud = ServiceRequest.query.get(request_id)
        service_rq_ud.remark = remarks
        service_rq_ud.date_of_completion = date.today()
        service_rq_ud.service_status = "Completed"
        db.session.commit()
    return render_template('close_it.html', service_request=service_rq)

@app.route('/search_customer', methods=['GET', 'POST'])
def search_customer():
    if request.method == 'POST':
        service_id = request.form['service_id']
        service_requests = db.session.query(
            ServiceRequest.id,
            ServiceRequest.service_id,
            ServiceRequest.customer_id,
            ServiceRequest.professional_id,
            ServiceRequest.date_of_request,
            ServiceRequest.service_status,
            ServiceRequest.remark
        ).filter(ServiceRequest.service_id == service_id).all()
        return render_template('search_customer.html', service_requests=service_requests, services=Service.query.all())
    services = Service.query.all()
    return render_template('search_customer.html', services=services, service_requests=None)

@app.route('/cust_sum')
def cust_sum():
    user = getUserInfo()
    if user['role'] == 'Admin':
        accepted_count = db.session.query(ServiceRequest).filter_by(service_status='Accepted').count()
        requested_count = db.session.query(ServiceRequest).filter_by(service_status='Requested').count()
        completed_count = db.session.query(ServiceRequest).filter_by(service_status='Completed').count()
    elif user['role'] == 'Professional':
        professional_id = user['id']
        accepted_count = db.session.query(ServiceRequest).filter_by(service_status='Accepted', professional_id=professional_id).count()
        requested_count = db.session.query(ServiceRequest).filter_by(service_status='Requested', professional_id=professional_id).count()
        completed_count = db.session.query(ServiceRequest).filter_by(service_status='Completed', professional_id=professional_id).count()
    elif user['role'] == 'Customer': 
        customer_id = user['id']
        accepted_count = db.session.query(ServiceRequest).filter_by(service_status='Accepted', customer_id=customer_id).count()
        requested_count = db.session.query(ServiceRequest).filter_by(service_status='Requested', customer_id=customer_id).count()
        completed_count = db.session.query(ServiceRequest).filter_by(service_status='Completed', customer_id=customer_id).count()
    statuses = ['Accepted', 'Requested', 'Completed']
    counts = [accepted_count, requested_count, completed_count]
    plt.figure(figsize=(6, 4))
    plt.bar(statuses, counts, color=['blue', 'orange', 'green'])
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.tight_layout()
    chart_path = 'static/cust_sum.png'
    plt.savefig(chart_path)
    plt.close()
    return render_template('cust_sum.html', chart_path=chart_path,user=user)

@app.route('/prof_search', methods=['GET', 'POST'])
def prof_search():
    user = getUserInfo()
    if user['role'] == 'Professional':
        requests = []
        if request.method == 'POST':
            pincode = request.form.get('pincode')
            
            if pincode:
                service_requests = db.session.query(
                    ServiceRequest.id,
                    ServiceRequest.service_id,
                    ServiceRequest.customer_id,
                    ServiceRequest.date_of_request,
                    ServiceRequest.service_status,
                    Customer.name.label('customer_name'),
                    Customer.address.label('customer_address'),
                    Customer.pincode.label('customer_pincode'),
                    Service.name.label('service_name')
                ).join(Customer, ServiceRequest.customer_id == Customer.id).join(             Service, ServiceRequest.service_id == Service.id).filter(ServiceRequest.professional_id == user['id'], Customer.pincode == pincode ).all()
                for sr in service_requests:
                    
                    serviceRequest_data = {
                        'id': sr.id,
                        'service_id': sr.service_id,
                        'customer_id': sr.customer_id,
                        'date_of_request': sr.date_of_request,
                        'service_status': sr.service_status,
                        'customer_name': sr.customer_name,
                        'customer_address': sr.customer_address,
                        'customer_pincode': sr.customer_pincode,
                        'service_name': sr.service_name
                    }
                    requests.append(serviceRequest_data)
            
                
            else:
                print("No pincode provided.")
        return render_template('prof_search.html', requests=requests)




if __name__ == '__main__':
    
    app.run(debug=True)


    


    