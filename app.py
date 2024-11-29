from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from sqlalchemy import text

import random
import datetime

app = Flask(__name__)
metrics = PrometheusMetrics(app)

metrics.info("app_info", "Application info", version="1.0.3")

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/otp_db'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///otp_db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class OTP(db.Model):
    __tablename__ = "otp"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="active")


with app.app_context():
    db.create_all()


@app.route("/otp", methods=["GET"])
def generate_otp():
    num_otps = random.randint(100, 200)
    otps = []
    for _ in range(num_otps):
        random_number = random.randint(100000, 999999)
        new_otp = OTP(number=random_number, status="active")
        db.session.add(new_otp)
        otps.append(str(random_number))  # Collect OTP as string

    db.session.commit()

    # Return HTML page with OTPs displayed as comma-separated values
    otp_list = ", ".join(otps)
    return render_template("otp_display.html", otp_list=otp_list)


@app.route("/", methods=["GET"])
def view_duplicates():
    try:
        result = db.session.execute(
            text(
                """
                SELECT number, COUNT(number) AS duplix 
                FROM otp 
                GROUP BY number 
                ORDER BY duplix DESC
                limit 10
            """
            )
        )

        duplicates = [{"number": row[0], "duplix": row[1]} for row in result.fetchall()]

        # return jsonify(duplicates), 200
        return render_template("duplicates.html", duplicates=duplicates)
    except Exception:
        import traceback

        traceback.print_exc()
        return jsonify({}), 500


if __name__ == "__main__":
    app.run(debug=False)
