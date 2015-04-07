from flask import Flask
from flask import render_template
from flask import request, redirect

import boto.ec2



app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("create_form.html")

@app.route('/create_instance')
def create_instance():
    conn = boto.ec2.connect_to_region("us-west-2", aws_access_key_id=request.args.get('access'), aws_secret_access_key=request.args.get('secret'))
    reservation = conn.run_instances('ami-815475b1',  instance_type='t1.micro')
    url_redirect = "/instance_status?access=" + request.args.get('access') + "&secret=" + request.args.get('secret') + "&id=" + reservation.instances[0].id
    return redirect(url_redirect, code=302)

@app.route('/terminate_instance')
def create_instance():
    conn = boto.ec2.connect_to_region("us-west-2", aws_access_key_id=request.args.get('access'), aws_secret_access_key=request.args.get('secret'))
    conn.terminate_instances(instance_ids=[request.args.get('id')])
    return render_template("status.html", status=status_code, link=link)

@app.route('/instance_status')
def instance_status():
    conn = boto.ec2.connect_to_region("us-west-2", aws_access_key_id=request.args.get('access'), aws_secret_access_key=request.args.get('secret'))
    status = conn.get_all_instance_status(instance_ids=[request.args.get('id')])
    try:
        status_code = status[0].state_code
    except:
        status_code = -1
    link = conn.get_all_instances(instance_ids=[request.args.get('id')])[0].instances[0].public_dns_name
    terminate_link =  "/terminate_instance?access=" + request.args.get('access') + "&secret=" + request.args.get('secret') + "&id=" + reservation.instances[0].id
    return render_template("status.html", status=status_code, link=link, terminate_link=terminate_link)


if __name__ == '__main__':
    app.debug = True
    app.run()