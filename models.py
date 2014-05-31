"""
Created on 03/02/2014

@author: Herminio
"""
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, BOOLEAN, DATE, Float
from sqlalchemy.orm import relationship, backref
from abc import abstractmethod
from app import db
import datetime

# Only for many-to-many relationship between Dataset and Indicator
dataset_indicator = db.Table('dataset_indicator',
    Column('dataset_id', String(255), ForeignKey('datasets.id')),
    Column('indicator_id', String(255), ForeignKey('indicators.id'))
)


class Language(db.Model):
    """ Language class. Contains language name and two-character code
    """
    __tablename__ = 'languages'
    lang_code = Column(String(2), primary_key=True, autoincrement=False)
    name = Column(String(25))

    def __init__(self, name, lang_code):
        self.name = name
        self.lang_code = lang_code


class RegionTranslation(db.Model):
    """Contains translations for country names
    """
    __tablename__ = 'regionTranslations'
    lang_code = Column(String(2), ForeignKey('languages.lang_code'), primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'), primary_key=True)
    name = Column(String(255))

    def __init__(self, lang_code, name, region_id=None):
        self.lang_code = lang_code
        self.region_id = region_id
        self.name = name

    def __str__(self):
        return '<RegionTranslation, name=' + self.name + ', lang_code=' + self.lang_code +'>'


class User(db.Model):
    """
    User model object
    """
    __tablename__ = "users"
    id = Column(String(255), primary_key=True, autoincrement=False)
    ip = Column(String(50))
    timestamp = Column(TIMESTAMP)
    organization_id = Column(String(255), ForeignKey('organizations.id'))
    organization = relationship("Organization", backref="users")

    def __init__(self, id=None, ip=None, timestamp=None, organization_id=None):
        """
        Constructor for user model object
        """
        self.id = id
        self.ip = ip
        self.timestamp = timestamp
        self.organization_id = organization_id


class OrganizationTranslation(db.Model):
    """Contains translations for organization names and descriptions
    """
    __tablename__ = 'organizationTranslations'
    lang_code = Column(String(2), ForeignKey('languages.lang_code'), primary_key=True)
    organization_id = Column(String(255), ForeignKey('organizations.id'), primary_key=True)
    description = Column(String(6000))

    def __init__(self, lang_code, description, organization_id=None):
        self.lang_code = lang_code
        self.organization_id = organization_id
        self.description = description


class Organization(db.Model):
    """
    classdocs
    """
    __tablename__ = "organizations"
    id = Column(String(255), primary_key=True, autoincrement=False)
    name = Column(String(128))
    url = Column(String(255))
    is_part_of_id = Column(String(255), ForeignKey("organizations.id"))
    is_part_of = relationship("Organization", uselist=False, foreign_keys=is_part_of_id)
    translations = relationship('OrganizationTranslation')

    def __init__(self, id=None, name=None, is_part_of=None, url=None):
        """
        Constructor
        """
        self.id = id
        self.name = name
        self.is_part_of = is_part_of
        self.data_sources = []
        self.url = url

    def add_data_source(self, data_source):
        self.data_sources.append(data_source)
        data_source.organization = self

    def add_translation(self, translation):
        translation.organization_id = self.id
        self.translations.append(translation)


class DataSource(db.Model):
    """
    classdocs
    """
    __tablename__ = "datasources"
    id = Column(String(255), primary_key=True)
    name = Column(String(128))
    organization_id = Column(String(255), ForeignKey("organizations.id"))
    organization = relationship("Organization", backref="sources")

    def __init__(self, name=None, organization=None, dsource_id=None):
        """
        Constructor
        """
        self.name = name
        self.organization = organization
        self.datasets = []
        self.observations = []
        self.dsource_id = dsource_id
        self.id = dsource_id

    def add_dataset(self, dataset):
        self.datasets.append(dataset)
        dataset.source = self

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.provider = self


class Dataset(db.Model):
    """
    classdocs
    """
    __tablename__ = 'datasets'
    id = Column(String(255), primary_key=True, autoincrement=False)
    sdmx_frequency = Column(String(255))
    datasource_id = Column(String(255), ForeignKey("datasources.id"))
    datasource = relationship("DataSource", backref="datasets")
    license_id = Column(Integer, ForeignKey("licenses.id"))
    license = relationship("License")
    indicators = relationship('Indicator',
                              secondary=dataset_indicator,
                              backref='datasets')

    def __init__(self, data_set_id=None, frequency=None, source=None):
        """
        Constructor
        """
        self.id = data_set_id
        self.frequency = frequency
        self.source = source
        self.slices = []

    def add_slice(self, data_slice):
        self.slices.append(data_slice)
        data_slice.dataset = self

    def add_indicator(self, indicator):
        self.indicators.append(indicator)


class Slice(db.Model):
    """
    classdocs
    """
    __tablename__ = "slices"
    id = Column(String(255), primary_key=True, autoincrement=False)
    indicator_id = Column(String(255), ForeignKey("indicators.id"))
    indicator = relationship("Indicator")
    dimension_id = Column(Integer, ForeignKey("dimensions.id"))
    dimension = relationship("Dimension")
    dataset_id = Column(String(255), ForeignKey("datasets.id"))
    dataset = relationship("Dataset", backref="slices")
    observations = relationship("Observation")

    def __init__(self, id, dimension=None, dataset=None, indicator=None):
        """
        Constructor
        """
        self.id = id
        self.dimension = dimension
        self.dataset = dataset
        self.indicator = indicator
        self.observations = []

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.data_slice = self


class Observation(db.Model):
    """
    classdocs
    """
    __tablename__ = "observations"
    id = Column(String(255), primary_key=True)
    ref_time_id = Column(Integer, ForeignKey("times.id"))
    ref_time = relationship("Time", foreign_keys=ref_time_id, uselist=False)
    issued_id = Column(Integer, ForeignKey("instants.id"))
    issued = relationship("Instant", foreign_keys=issued_id, uselist=False)
    computation_id = Column(Integer, ForeignKey("computations.id"))
    computation = relationship("Computation", foreign_keys=computation_id)
    indicator_group_id = Column(String(255), ForeignKey("indicatorGroups.id"))
    indicator_group = relationship("IndicatorGroup", foreign_keys=indicator_group_id)
    value_id = Column(Integer, ForeignKey("values.id"))
    value = relationship("Value", foreign_keys=value_id, uselist=False)
    indicator_id = Column(String(255), ForeignKey("indicators.id"))
    indicator = relationship("Indicator", foreign_keys=indicator_id)
    dataset_id = Column(String(255), ForeignKey("datasets.id"))
    dataset = relationship("Dataset", foreign_keys=dataset_id, backref="observations")
    region_id = Column(Integer, ForeignKey("regions.id"))
    slice_id = Column(String(255), ForeignKey("slices.id"))

    def __init__(self, id=None, ref_time=None, issued=None,
                 computation=None, value=None, indicator=None, provider=None):
        """
        Constructor
        """
        self.id = id
        self.ref_time = ref_time
        self.issued = issued
        self.computation = computation
        self.value = value
        self.indicator = indicator
        self.provider = provider

    def __str__(self):
        return "<Observation(id_source='%s', ref_time='%s', issued='%s', " \
               "computation='%s', value='%s', indicator='%s', provider='%s')>" % \
               (self.id_source, self.ref_time, self.issued, self.computation,
                self.value, self.indicator, self.provider)


class Indicator(db.Model):
    """
    classdocs
    """
    __tablename__ = "indicators"
    id = Column(String(255), primary_key=True)
    preferable_tendency = Column(String(100))
    measurement_unit_id = Column(Integer, ForeignKey("measurementUnits.id"))
    measurement_unit = relationship("MeasurementUnit")
    compound_indicator_id = Column(String(255), ForeignKey("compoundIndicators.id"))
    last_update = Column(TIMESTAMP)
    starred = Column(BOOLEAN)
    type = Column(String(50))
    topic_id = Column(String(100), ForeignKey('topics.id'))
    translations = relationship('IndicatorTranslation')

    __mapper_args__ = {
        'polymorphic_identity': 'indicators',
        'polymorphic_on': type
    }

    def __init__(self, id, preferable_tendency=None, measurement_unit_id=None,
            dataset_id=None, compound_indicator_id=None, starred=False):
        self.id = id
        self.preferable_tendency = preferable_tendency
        self.measurement_unit_id = measurement_unit_id
        self.dataset_id = dataset_id
        self.compound_indicator_id = compound_indicator_id
        self.starred = starred

    def __repr__(self):
        return "<Indicator(id='%s', id_source='%s', name='%s', description='%s', " \
               "measurement_unit_id='%s', dataset_id='%s', type='%s')>" % \
               (self.id, self.id_source, self.name, self.description, self.measurement_unit_id,
                self.dataset_id, self.type)

    def add_translation(self, translation):
        translation.indicator_id = self.id
        self.translations.append(translation)


class IndicatorTranslation(db.Model):
    """Contains translations for indicator names and descriptions
    """
    __tablename__ = 'indicatorTranslations'
    lang_code = Column(String(2), ForeignKey('languages.lang_code'), primary_key=True)
    indicator_id = Column(String(255), ForeignKey('indicators.id'), primary_key=True)
    name = Column(String(6000))
    description = Column(String(6000)) #Hope it is enough...

    def __init__(self, lang_code, name, description, indicator_id=None):
        self.lang_code = lang_code
        self.indicator_id = indicator_id
        self.name = name
        self.description = description


class Topic(db.Model):
    """Topic class. Each indicator refers to a topic
    """
    __tablename__ = 'topics'
    id = Column(String(100), primary_key=True, autoincrement=False)
    indicators = relationship('Indicator', backref='topic')
    translations = relationship('TopicTranslation')

    def __init__(self, id):
        self.id = id
        self.indicators = []
        self.translations = []

    def add_translation(self, translation):
        self.translations.append(translation)
        translation.topic_id = self.id


class TopicTranslation(db.Model):
    """Contains translations for topic names
    """
    __tablename__ = 'topicTranslations'
    lang_code = Column(String(2), ForeignKey('languages.lang_code'), primary_key=True)
    topic_id = Column(String(100), ForeignKey('topics.id'), primary_key=True)
    name = Column(String(6000))

    def __init__(self, lang_code, name, topic_id=None):
        self.lang_code = lang_code
        self.topic_id = topic_id
        self.name = name


class IndicatorGroup(db.Model):
    """
    classdocs
    """
    __tablename__ = "indicatorGroups"
    id = Column(String(255), primary_key=True)
    observations = relationship("Observation")

    __mapper_args__ = {
        'polymorphic_identity': 'indicatorGroups',
    }


class MeasurementUnit(db.Model):
    """
    classdocs
    """
    __tablename__ = "measurementUnits"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    convertible_to = Column(String(255))
    factor = Column(Float)

    def __init__(self, id=None, name=None, convertible_to=None, factor=None):
        self.id = id
        self.name = name
        self.convertible_to = convertible_to
        self.factor = factor

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, MeasurementUnit):
            return self.name == other.name
        else:
            return False


class License(db.Model):
    """
    classdocs
    """
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True)
    name = Column(String(6000))
    description = Column(String(6000))
    republish = Column(BOOLEAN)
    url = Column(String(500))

    def __init__(self, name=None, description=None, republish=None, url=None):
        """
        Constructor
        """
        self.name = name
        self.description = description
        self.republish = republish
        self.url = url


class Computation(db.Model):
    """
    classdocs
    """
    __tablename__ = "computations"
    id = Column(Integer, primary_key=True)
    uri = Column(String(500))
    description = Column(String(6000))

    def __init__(self, uri=None, description=None):
        """
        Constructor
        """
        self.uri = uri
        self.description = description


class Value(db.Model):
    """
    classdocs
    """
    __tablename__ = "values"
    id = Column(Integer, primary_key=True)
    obs_status = Column(String(500))
    value_type = Column(String(50))
    value = Column(String(500))

    def __init__(self, obs_status=None):
        """
        Constructor
        """
        self.obs_status = obs_status


class IndicatorRelationship(db.Model):
    """
    classdocs
    """
    __tablename__ = "indicatorRelationships"
    id = Column(Integer, primary_key=True)
    source_id = Column(String(255), ForeignKey("indicators.id"))
    source = relationship("Indicator", foreign_keys=source_id)
    target_id = Column(String(255), ForeignKey("indicators.id"))
    target = relationship("Indicator", foreign_keys=target_id)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'indicatorRelationships',
        'polymorphic_on': type
    }

    def __init__(self, source=None, target=None):
        """
        Constructor
        """
        self.source = source
        self.target = target


class IsPartOf(IndicatorRelationship):
    """
    classdocs
    """
    __tablename__ = "ispartof"
    id = Column(Integer, ForeignKey("indicatorRelationships.id"), primary_key=True)
    source_id = Column(String(255), ForeignKey("indicators.id"))
    target_id = Column(String(255), ForeignKey("indicators.id"))

    __mapper_args__ = {
        'polymorphic_identity': 'ispartof',
    }


    def __init__(self, source=None, target=None):
        """
        Constructor
        """
        super(IsPartOf, self).__init__(source, target)


class Becomes(IndicatorRelationship):
    """
    classdocs
    """
    __tablename__ = "becomes"
    id = Column(Integer, ForeignKey("indicatorRelationships.id"), primary_key=True)
    source_id = Column(String(255), ForeignKey("indicators.id"))
    target_id = Column(String(255), ForeignKey("indicators.id"))

    __mapper_args__ = {
        'polymorphic_identity': 'becomes',
    }

    def __init__(self, source=None, target=None):
        """
        Constructor
        """
        super(Becomes, self).__init__(source, target)


class Dimension(db.Model):
    """
    classdocs
    """
    __tablename__ = "dimensions"
    id = Column(Integer, primary_key=True)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'dimensions',
        'polymorphic_on': type
    }

    @abstractmethod
    def get_dimension_string(self): pass


class Time(Dimension):
    """
    classdocs
    """
    __tablename__ = "times"
    id = Column(Integer, ForeignKey("dimensions.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'times',
    }

    @abstractmethod
    def get_time_string(self): pass

    def get_dimension_string(self):
        return self.get_time_string()


class Instant(Time):
    """
    classdocs
    """
    __tablename__ = "instants"
    id = Column(Integer, ForeignKey("times.id"), primary_key=True)
    timestamp = Column(TIMESTAMP)

    __mapper_args__ = {
        'polymorphic_identity': 'instants',
    }

    def __init__(self, instant=None):
        """
        Constructor
        """
        self.timestamp = instant

    def get_time_string(self):
        return self.instant.strftime("%Y-%m-%dT%H:%M:%S")


class Interval(Time):
    """Represents any interval of time"""
    __tablename__ = "intervals"
    id = Column(Integer, ForeignKey("times.id"), primary_key=True)
    start_time = Column(DATE)
    end_time = Column(DATE)
    value = Column(String(60))

    __mapper_args__ = {
        'polymorphic_identity': 'intervals',
    }

    def __init__(self, start_time=None, end_time=None):
        """Expects 'start_time' and 'end_time' as datetime.date objects"""
        self.start_time = start_time
        self.end_time = end_time
        if self.start_time is not None and self.end_time is not None:
            self.value = str(self.start_time.year) + "-" + str(self.end_time.year)

    def get_time_string(self):
        return self.value


class YearInterval(Interval):
    """Represents a single year"""
    __tablename__ = "yearIntervals"
    id = Column(Integer, ForeignKey("intervals.id"), primary_key=True)
    start_time = Column(DATE)
    end_time = Column(DATE)
    year = Column(Integer)
    value = Column(String(60))

    __mapper_args__ = {
        'polymorphic_identity': 'yearIntervals',
    }

    def __init__(self, year):
        """Expects 'year' as an integer or as an string"""
        self.year = int(year)
        self.value = str(self.year)
        self.start_time = datetime.date(year=self.year, month=1, day=1)
        self.end_time = datetime.date(year=self.year+1, month=1, day=1)
        #super(YearInterval, self).__init__(self.start_time, self.end_time)

    def get_time_string(self):
        return self.value


class MonthInterval(Interval):
    """Represents a single month"""
    __tablename__ = "monthIntervals"
    id = Column(Integer, ForeignKey("intervals.id"), primary_key=True)
    start_time = Column(DATE)
    end_time = Column(DATE)
    year = Column(Integer)
    month = Column(Integer)
    value = Column(String(60))

    __mapper_args__ = {
        'polymorphic_identity': 'monthIntervals',
    }

    def __init__(self, month, year):
        """Expects 'month' and 'year' as an integer or as a string"""
        self.year = int(year)
        self.month = int(month)
        self.value = str(self.year) +"-"+ str(self.month)
        self.start_time = datetime.date(year=self.year, month=self.month, day=1)
        if self.month == 12:
            self.end_time = datetime.date(year=self.year+1, month=1, day=1)
        else:
            self.end_time = datetime.date(year=self.year, month=self.month+1, day=1)
        #super(YearInterval, self).__init__(self.start_time, self.end_time)

    def get_time_string(self):
        return self.value


class Region(Dimension):
    """
    classdocs
    """
    __tablename__ = "regions"
    id = Column(Integer, ForeignKey("dimensions.id"), primary_key=True)
    un_code = Column(Integer)
    is_part_of_id = Column(Integer, ForeignKey("regions.id"))
    is_part_of = relationship("Region", uselist=False, foreign_keys=is_part_of_id)
    observations = relationship("Observation")
    translations = relationship('RegionTranslation')

    __mapper_args__ = {
        'polymorphic_identity': 'regions',
    }

    def __init__(self, is_part_of=None, un_code=None):
        """
        Constructor
        """
        self.un_code = un_code
        self.is_part_of = is_part_of
        self.observations = []

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.region = self

    def get_dimension_string(self):
        return str(self.id)

    def add_translation(self, translation):
        self.translations.append(translation)
        translation.region_id = self.id


class Country(Region):
    """
    classdocs
    """
    __tablename__ = "countries"
    id = Column(Integer, ForeignKey("regions.id"), primary_key=True)
    is_part_of_id = Column(Integer)
    faoURI = Column(String(500))
    iso2 = Column(String(2))
    iso3 = Column(String(3))

    __mapper_args__ = {
        'polymorphic_identity': 'countries',
    }

    def __init__(self, iso2=None, iso3=None, fao_URI=None, is_part_of=None,
                 un_code=None):
        """
        Constructor
        """
        super(Country, self).__init__(is_part_of, un_code)
        self.iso2 = iso2
        self.iso3 = iso3
        self.faoURI = fao_URI

    def get_dimension_string(self):
        return self.iso3


class CompoundIndicator(Indicator):
    """
    classdocs
    """
    # There was a problem with a circular dependency whith this table.
    # Solution consisted in indicate the joins explicitly. Look at:
    #   - indicator_refs
    #   - inherit_condition
    __tablename__ = "compoundIndicators"
    id = Column(String(255),
                primary_key=True)
    indicator_id = Column(Integer)
    measurement_unit_id = Column(Integer, ForeignKey("measurementUnits.id"))
    dataset_id = Column(String(255), ForeignKey("datasets.id"))
    indicator_refs = relationship("Indicator", primaryjoin="CompoundIndicator.id == Indicator.compound_indicator_id") #circular dependency
    indicator_ref_group_id = Column(String(255), ForeignKey("indicatorGroups.id"))
    indicator_ref_group = relationship("IndicatorGroup", foreign_keys=indicator_ref_group_id,
                                       backref=backref("compound_indicator", uselist=False))
    last_update = Column(TIMESTAMP)
    starred = Column(BOOLEAN)

    __mapper_args__ = {
        'polymorphic_identity': 'compoundIndicators',
        'inherit_condition': (id == Indicator.id),
    }

    def __repr__(self):
        return '<CompoundIndicator: id={}'.format(self.id)


class Auth(db.Model):
    __tablename__ = "auth"
    user = Column(String(256), primary_key=True)
    token = Column(String(256))

    def __init__(self, user, token):
        self.user = user
        self.token = token
