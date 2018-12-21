from app import db
from app.models import Schedule_year, Role, Team, User, User_schedule
from app.admin.views import import_schedule_data


def create_first_year():
    year8 = Schedule_year()
    year8.year = '2018'
    year8.start_date = '2017-12-31'
    year8.end_date = '2018-12-31'
    year8.iscurrent = True

    year7 = Schedule_year()
    year7.year = '2017'
    year7.start_date = '2017-12-30'
    year7.end_date = '2016-12-31'
    year7.iscurrent = False

    year9 = Schedule_year()
    year9.year = '2019'
    year9.start_date = '2019-01-01'
    year9.end_date = '2019-12-31'
    year9.iscurrent = False

    db.session.add(year7)
    db.session.add(year8)
    db.session.add(year9)
    db.session.commit()


def create_users():
    users = [
        {
            'confirmed': True,
            'first_name': 'Sydney',
            'last_name': 'Lo',
            'email': 'slo@squirrelsystems.com',
            'phone': '604-845-1454',
            'active': True,
            'start_date': '2014-09-12',
            'role': Role.query.filter_by(name='User').first(),
            'team': Team.query.filter_by(name='SC').first(),
            'years': ['2017', '2018'],
            'carriedvacation': 8,
            'entitledvacation': 15,
            'entitledpersonal': 9,
            'isparttime': False,
            'isaveraging': False,
            'shiftlength': 8
        },
        {
            'confirmed': True,
            'first_name': 'Chris',
            'last_name': 'Brooks',
            'email': 'cbrooks@squirrelsystems.com',
            'phone': '604-845-1222',
            'active': True,
            'start_date': '2016-09-12',
            'role': Role.query.filter_by(name='Administrator').first(),
            'team': Team.query.filter_by(name='SC').first(),
            'years': ['2018'],
            'carriedvacation': 8,
            'entitledvacation': 15,
            'entitledpersonal': 9,
            'isparttime': False,
            'isaveraging': True,
            'shiftlength': 12
        },
        {
            'confirmed': True,
            'first_name': 'Jason',
            'last_name': 'Babcock',
            'email': 'jbabcock@squirrelsystems.com',
            'phone': '604-845-5555',
            'active': True,
            'start_date': '2011-09-12',
            'role': Role.query.filter_by(name='User').first(),
            'team': Team.query.filter_by(name='ES').first(),
            'years': ['2018'],
            'carriedvacation': 8,
            'entitledvacation': 15,
            'entitledpersonal': 9,
            'isparttime': False,
            'isaveraging': False,
            'shiftlength': 8
        },
        {
            'confirmed': True,
            'first_name': 'Jacky',
            'last_name': 'Ho',
            'email': 'jho@squirrelsystems.com',
            'phone': '604-845-5555',
            'active': True,
            'start_date': '2012-09-12',
            'role': Role.query.filter_by(name='User').first(),
            'team': Team.query.filter_by(name='CS').first(),
            'years': ['2018'],
            'carriedvacation': 8,
            'entitledvacation': 15,
            'entitledpersonal': 9,
            'isparttime': False,
            'isaveraging': False,
            'shiftlength': 8
        },
        {
            'confirmed': False,
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'email': 'jsparrow@squirrelsystems.com',
            'phone': '604-845-5555',
            'active': True,
            'start_date': '2014-09-12',
            'role': Role.query.filter_by(name='User').first(),
            'team': Team.query.filter_by(name='SC').first(),
            'years': ['2018'],
            'carriedvacation': 8,
            'entitledvacation': 15,
            'entitledpersonal': 9,
            'isparttime': True,
            'isaveraging': False,
            'shiftlength': 8
        },
        {
            'confirmed': True,
            'first_name': 'Michael',
            'last_name': 'Chung',
            'email': 'mchung@squirrelsystems.com',
            'phone': '604-845-2222',
            'active': False,
            'start_date': '2015-09-12',
            'role': Role.query.filter_by(name='User').first(),
            'team': Team.query.filter_by(name='SC').first(),
            'years': ['2018'],
            'carriedvacation': 8,
            'entitledvacation': 15,
            'entitledpersonal': 9,
            'isparttime': False,
            'isaveraging': False,
            'shiftlength': 8
        },
        {
            'confirmed': True,
            'first_name': 'Ramon',
            'last_name': 'Estupe',
            'email': 'restupe@squirrelsystems.com',
            'phone': '604-845-2222',
            'active': True,
            'start_date': '2015-09-12',
            'role': Role.query.filter_by(name='User').first(),
            'team': Team.query.filter_by(name='SC').first(),
            'years': ['2018'],
            'carriedvacation': 8,
            'entitledvacation': 15,
            'entitledpersonal': 9,
            'isparttime': False,
            'isaveraging': False,
            'shiftlength': 8
        },
    ]
    for u in users:
        user = User()
        user.first_name = u['first_name']
        user.last_name = u['last_name']
        user.confirmed = u['confirmed']
        user.email = u['email']
        user.phone = u['phone']
        user.active = u['active']
        user.start_date = u['start_date']
        user.role = u['role']
        user.team = u['team']
        if u['confirmed']:
            for year in u['years']:
                year = Schedule_year.query.filter_by(year=year).first()
                user_sched = User_schedule()
                user_sched.year = year
                user_sched.user = user
                if year.iscurrent:
                    user_sched.active = True
                else:
                    user_sched.active = False
                user_sched.carriedvacation = u['carriedvacation']
                user_sched.entitledvacation = u['entitledvacation']
                user_sched.entitledpersonal = u['entitledpersonal']
                user_sched.isparttime = u['isparttime']
                user_sched.isaveraging = u['isaveraging']
                user_sched.shiftlength = u['shiftlength']

        db.session.add(user)
        db.session.commit()


def create_shifts_time_off():
    #_2017 = open('tests/2017_schedule.xlsx', 'rb')
    _2018 = open('tests/2018_schedule.xlsx', 'rb')
    #import_schedule_data(_2017, '2017')
    import_schedule_data(_2018, '2018')


def create_demo_data():
    create_first_year()
    create_users()
    create_shifts_time_off()
