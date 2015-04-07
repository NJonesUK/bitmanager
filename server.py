from flask import Flask
from flask import render_template
from flask import request, redirect

import boto.ec2

app = Flask(__name__)

# Default homepage - requests credentials to perform the instance creation with
@app.route('/')
def hello_world():
    return render_template("create_form.html")

# Creates a Bitnami Wordpress instance
@app.route('/create_instance',  methods=['GET', 'POST'])
def create_instance():
    try:
        conn = boto.ec2.connect_to_region("us-west-2", aws_access_key_id=request.args.get('access'), aws_secret_access_key=request.args.get('secret'))
        reservation = conn.run_instances('ami-815475b1',  instance_type='t1.micro')
        url_redirect = "/instance_status?access=" + request.args.get('access') + "&secret=" + request.args.get('secret') + "&id=" + reservation.instances[0].id
        return redirect(url_redirect, code=302)
    except Exception, e:
        return "Something went wrong, check your supplied AWS credentials"


# Terminates the supplied instance ID
@app.route('/terminate_instance')
def terminate_instance():
    try:
        conn = boto.ec2.connect_to_region("us-west-2", aws_access_key_id=request.args.get('access'), aws_secret_access_key=request.args.get('secret'))
        conn.terminate_instances(instance_ids=[request.args.get('id')])
        return render_template("terminated.html")
    except Exception, e:
        return "Something went wrong, check your supplied AWS credentials"


# Get instance status - still buggy, for some reason the only status returned is "running", pending, terminated and the like do not correctly show.
@app.route('/instance_status')
def instance_status():
    try:
        conn = boto.ec2.connect_to_region("us-west-2", aws_access_key_id=request.args.get('access'), aws_secret_access_key=request.args.get('secret'))
        reservations = conn.get_all_reservations(instance_ids=[request.args.get('id')])
    except Exception, e:
        return "Something went wrong, check your supplied AWS credentials"

    status = conn.get_all_instance_status(instance_ids=[request.args.get('id')])
    try:
        status_code = status[0].state_code
    except:
        status_code = -1
    link = conn.get_all_instances(instance_ids=[request.args.get('id')])[0].instances[0].public_dns_name
    terminate_link =  "/terminate_instance?access=" + request.args.get('access') + "&secret=" + request.args.get('secret') + "&id=" + conn.get_all_instances(instance_ids=[request.args.get('id')])[0].instances[0].id
    return render_template("status.html", status=status_code, link=link, terminate_link=terminate_link)


if __name__ == '__main__':
    app.debug = True
    app.run()