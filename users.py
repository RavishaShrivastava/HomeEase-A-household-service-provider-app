from flask import session
from model import Customer, Professional, Admin, Service, ServiceRequest
from app import db
def getUserInfo():
    if 'id' in session:
        u = Customer.query.filter_by(id=session['id']).first()
        s = Professional.query.filter_by(id=session['id']).first()
        a = Admin.query.filter_by(id=session['id']).first()
        if u and session['eemail'] == u.email:
            id=u.id
            email=u.email
            role='Customer'
            name=u.name
            address=u.address
            pincode=u.pincode
            d={'id':id,'email':email,'role':role,'name':name,'address':address,'pincode':pincode}
            return d
        elif s and session['eemail'] == s.email:
            id=s.id
            email=s.email
            role='Professional'
            name=s.name
            service=s.service
            experience=s.experience
            address=s.address
            pincode=s.pincode
            status=s.status
            d={'id':id,'email':email,'role':role,'name':name,'service':service,'experience':experience,'address':address,'pincode':pincode,'status':status}
            return d
        elif a and session['eemail'] == a.email:
            id=a.id
            email=a.email
            name=a.name
            role='Admin'
            d={'id':id,'email':email,'role':role,'name':name}
            return d
        else:
            return None
    else:
        return None

def getAllServices():
    services = Service.query.all()  
    service_list = []
    for service in services:
        service_data = {
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'description': service.description,
            'time': service.time
        }
        service_list.append(service_data)
    return service_list
def getAllProfessional():
    professionals = Professional.query.all()
    professional_list=[]
    for professional in professionals:
        professional_data = {
            'id': professional.id,
            'name':professional.name,
            'email':professional.email,
            'service': professional.service,
            'experience':professional.experience,
            'address': professional.address,
            'pincode':professional.pincode,
            'status':professional.status
        }
        professional_list.append(professional_data)
    return professional_list
def getServiceInfo():
    if 'services' in session and session['services']:
        services = Service.query.filter(Service.name.in_(session['services'])).all()
        if services:
            return [{'name': s.name, 'description': s.description, 'price': s.price} for s in services]
    return None
def getAllServiceRequest(professional_service):
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
    ).join(Customer, ServiceRequest.customer_id == Customer.id).join(Service, ServiceRequest.service_id == Service.id).filter(Service.name == professional_service).all()
    serviceRequest_list = []
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
        serviceRequest_list.append(serviceRequest_data)
    return serviceRequest_list

