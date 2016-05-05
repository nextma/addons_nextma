# -*- coding: utf-8 -*-

##############################################################################
#
#    NEXTMA SARL, Open Source Management Solution
#    Copyright (C) 2006-today (<http://www.nextma.com>)
#

##############################################################################

import datetime, time
from fractions import Fraction
import math

from openerp import tools,_
from openerp.osv import osv, fields


########## client ################################################################################
class res_partner(osv.osv):
    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['civilite_client','name','first_name'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['first_name']:
                name = str(record['civilite_client'])+' '+record['first_name']+' '+name
            res.append((record['id'], name))
        return res


    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)



    _columns = {
        'code_client' : fields.char(u'Code client',size=50),
        'civilite_client' : fields.selection([('Monsieur',u'Monsieur'),('Madame',u'Madame'),('Mademoiselle',u'Mademoiselle')],u'Civilité client'),
        'civilite_client_arab' : fields.selection([('Monsieur1',u'السيد'),('Madame1',u'السيدة'),('Mademoiselle1',u'الآنسة')],u'اللقب المدني'),
        'type_client' : fields.selection([('particuliers',u'Particuliers'),('administration',u'Administration'),('societe',u'Société'),('promotteur',u'Promotteur'),('banque',u'Banque')],u'Type client'),
        'patente_societe' : fields.char(u'Patente Société',size=50),
        'if_societe' : fields.char(u'IF Société',size=50),
        'cnss_societe' : fields.char(u'CNSS Société',size=50),
        'gerant_societe' : fields.many2one('res.partner',u'Gérant Société'),
        'rc_societe' : fields.char(u'RC Société',size=50),
        'patente_promotteur' : fields.char(u'Patente promotteur',size=50),
        'representant_administration' : fields.char(u'Représentant administration',size=50),
        'cin' : fields.char(u'N°CIN',size=50),
        'date_validation_cin' : fields.date(u'Date validation cin'),
        'first_name' : fields.char(u'Prénom',size=50),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Nom/Raison sociale', store=True),
        'first_name_arabic' : fields.char(u'الإسم الشخصي',size=50),
	    'name_arabic' : fields.char(u'اسم الشركة/الإسم العائلي',size=50),
        'lieu_naissance' : fields.char(u'Lieu naissance',size=50),
        'date_naissance' : fields.date(u'Date de naissance'),
        'nom_pere' : fields.char(u'Nom père',size=50),
        'nom_mere' : fields.char(u'Nom mère',size=50),
        'nom_epoux' : fields.char(u'Nom conjoint',size=50),
        'date_mariage' : fields.date(u'Date mariage'),
        'statut_marital' : fields.selection([('celibataire',u'Célibataire'),('marie',u'Marié(e)'),('divorce',u'Divorcé(e)'),('veuf',u'Veuf(ve)'),],u'Situation familiale', readonly=False),
        'date_creation_client' : fields.datetime(u'Date création client', readonly=True),
        'user_creation_id' : fields.many2one('res.users',u'Crée(e) par'),
        'proprietes_id': fields.one2many('proprietaire.bien', 'client_id', u'Propriétés liés'),
    }


    def _check_date_validation_cin(self, cr, uid, ids) :
        for client in self.browse(cr, uid, ids) :
            if client.type_client == 'particuliers' and client.date_validation_cin != False  :
                date_validation = client.date_validation_cin.split('-')
                date_mtn= time.strftime('%Y-%m-%d').split('-')
                jours1 = 0
                jours2 = 0
                jours1 = ((int(date_mtn[0]) * 365) + (int(date_mtn[1]) * 30) + int((date_mtn[2])))
                jours2 = ((int(date_validation[0]) * 365) + (int(date_validation[1]) * 30) + int((date_validation[2])))
                compteur = (jours2 - jours1)
                if compteur <= 0: return False
        return True

    _sql_constraints = [('cin_uniq','unique(cin)', 'CIN DOIT ETRE UNIQUE!')]

    _constraints = [(_check_date_validation_cin,'ERREUR : LA DATE DE VALIDATION DE LA CIN EST DÉPASSÉE !', ['date_validation_cin'])]

    _defaults = {

        'user_creation_id': lambda object,cr,uid,context: uid,
        'date_creation_client' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'statut_marital': 'celibataire',
        'type_client': 'particuliers',
        'code_client': '/',
    }

    def onchange_civilite_arab(self, cr, uid, ids, civilite_client_arab):
        result = {'value': {}}
        if civilite_client_arab == 'Monsieur1':
            result['value']['civilite_client'] = 'Monsieur'
        elif civilite_client_arab == 'Madame1':
            result['value']['civilite_client'] = 'Madame'
        elif civilite_client_arab == 'Mademoiselle1':
            result['value']['civilite_client'] = 'Mademoiselle'
        return result  



    def onchange_civilite(self, cr, uid, ids, civilite_client):
        result = {'value': {}}
        if civilite_client == 'Monsieur':
            result['value']['civilite_client_arab'] = 'Monsieur1'
        elif civilite_client == 'Madame':
            result['value']['civilite_client_arab'] = 'Madame1'
        elif civilite_client == 'Mademoiselle':
            result['value']['civilite_client_arab'] = 'Mademoiselle1'
        return result  




    def create(self, cr, uid, data, context=None):
        if ('code_client' not in data) or (data.get('code_client')=='/'):
            data['code_client'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
        if 'name' in data :
            data['name'] =  data['name'].upper()
        if 'first_name' in data and data['type_client']=='particuliers' : 
            data['first_name'] =  data['first_name'].upper()
        if 'cin' in data and data['type_client']=='particuliers' :
            data['cin'] =  data['cin'].upper().replace(' ', '')  
        return super(res_partner,self).create(cr, uid, data, context)



    def write(self, cr, user, ids, vals, context=None):
        if ('name' in vals)   :
            vals['name'] =  vals['name'].upper()
        if 'first_name' in vals :
            vals['first_name'] =  vals['first_name'].upper()
        if 'cin' in vals :
            vals['cin'] =  vals['cin'].upper().replace(' ', '')    
        return super(res_partner, self).write(cr, user, ids, vals,context=context)

res_partner()



####### appel telephonique entrant client ##################################
class appel_entrant(osv.osv):
    _name = 'appel.entrant'

    _columns = {

        'date_appel' : fields.datetime(u'Date appel',required=True),
        'objet_appel' : fields.char(u'Objet appel',size=50,required=True),
        'dossier_id' : fields.many2one('notariat.dossier',u'Dossier'),
        'user_id' : fields.many2one('res.users',u'Reçu(e) par',required=True),
        'client_id' : fields.many2one('res.partner',u'Client appelant'),
        'numero_telephone' : fields.char(u'Numero téléphone appelant',size=50),
        'personne_appelee' : fields.char(u'Personne appelant',size=50),
        'observation' : fields.char(u'Observations',size=50),


    }

    _defaults = {


        'date_appel' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda object,cr,uid,context: uid,


    }

    _order = "date_appel desc"

appel_entrant()


####### appel telephonique sortant client ##################################
class appel_sortant(osv.osv):
    _name = 'appel.sortant'

    _columns = {

        'date_appel' : fields.datetime(u'Date appel',required=True),
        'objet_appel' : fields.char(u'Objet appel',size=50,required=True),
        'dossier_id' : fields.many2one('notariat.dossier',u'Dossier'),
        'user_id' : fields.many2one('res.users',u'Effectué(e) par',required=True),
        'client_id' : fields.many2one('res.partner',u'Client'),
        'numero_telephone' : fields.char(u'Numero téléphone',size=50),
        'personne_appelee' : fields.char(u'Personne appelée',size=50),
        'observation' : fields.char(u'Observations',size=50),
    }

    _defaults = {
        'date_appel' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda object,cr,uid,context: uid,
    }

    _order = "date_appel desc"

appel_sortant()


#### visite client ###############################################
class visite_client(osv.osv):
    _name = 'visite.client'

    def _get_number_of_minutes(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        diff_min = diff_day * 1440
        return diff_min

    def _compute_number_of_min(self, cr, uid, ids, name, args, context=None):
        result = {}
        for visi in self.browse(cr, uid, ids, context=context):
            result[visi.id] = visi.number_of_min_temp
            print visi.number_of_min_temp
        print result
        return result


    def _get_date_visite(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.date_visite.strftime('%Y-%m-%d')
        return res 


    def _get_date_sortie(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.date_sortie.strftime('%Y-%m-%d')
        return res 


    _columns = {
        'date_visite_func': fields.function(_get_date_visite, method=True, type='date', string=u'Date visite client'),
        'date_sortie_func': fields.function(_get_date_sortie, method=True, type='date', string=u'Date sortie client'),
        'date_visite' : fields.datetime(u'Date visite client'),
        'client_id' : fields.many2one('res.partner',u'Client',required=True),
        'objet' : fields.char(u'Objet de la visite',size=50),
        'dossier_id' : fields.many2one('notariat.dossier',u'Dossier',domain="[('partie_id.partie_client_id.customer_id.id','in',[client_id])]"),
        'user_id' : fields.many2one('res.users',u'Pris en charge par',required=True),
        'date_sortie' : fields.datetime(u'Date sortie client'),
        'number_of_min_temp': fields.float(u'Durée en min'),
        'number_of_min': fields.function(_compute_number_of_min, string=u'Durée visite en minutes', store=True),
    }
    _defaults = {
        'date_visite' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda object,cr,uid,context: uid,
    }
    
    _order = "date_visite desc"


    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_min = self._get_number_of_minutes(date_from, date_to)
            result['value']['number_of_min_temp'] = round(math.floor(diff_min))+1
        else:
            result['value']['number_of_min_temp'] = 0

        return result



    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_min = self._get_number_of_minutes(date_from, date_to)
            result['value']['number_of_min_temp'] = round(math.floor(diff_min))+1
        else:
            result['value']['number_of_min_temp'] = 0

        return result

visite_client()


######### travail effectue #######################################################
class travail_effectue(osv.osv):

    _name = 'travail.effectue'
    _columns = {

        'name' : fields.char(u'Numéro travail',size=8),
        'libelle_travail' : fields.many2one('libelle.travail',u'Libellé',required=True),
        'demandeur_id' : fields.many2one('res.users',u'Demandeur',required=True),
        'executeur_id' : fields.many2one('res.users',u'Executeur',required=True),
        'date_demande' : fields.datetime(u'Demandé le',required=True),
        'date_realisation' : fields.datetime(u'Réalise le'),
        'observation' : fields.char(u'Observations',size=50),
        'dossier_id' : fields.many2one('notariat.dossier',u'Dossier',required=True),
        'state':fields.selection([('draft', u'Brouillon'), ('envoye', u'Envoyé'),('cancel', u'Annulé'),('execute', u'Executé'),], 'Etat Travail'),
    }

    def envoyer_mail_demande(self,cr,uid,ids,context={}):
        print "fonction envoi mail"
        for objet_travail in self.browse(cr,uid,ids):
            if objet_travail.state == 'draft':
                if objet_travail.executeur_id and objet_travail.executeur_id.email:
                    data_text = u"""<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
                    
                     <p>Bonjour %s,</p>
                     
                     <p>Vous avez reçu un ordre de travail de référence %s pour le dossier %s, demandé par %s à la date du %s. </p>
                     <p>Il concerne la description suivante : </p>
                     <p>%s</p>
                     <p>Prière de l'avertir en validant le travail une fois achevé</p>
                     """ %(objet_travail.executeur_id.name, objet_travail.name, objet_travail.dossier_id and objet_travail.dossier_id.name, objet_travail.demandeur_id.name,objet_travail.date_demande,objet_travail.libelle_travail.name)
                    data_mail={
                                                       'type' : 'email',
                                                       'subject' : u'Demande de travail',
                                                       'date' : time.strftime('%Y-%m-%d %H:%M:%S'),
                                                       'email_to' : objet_travail.executeur_id.email,
                                                       'body_html' : data_text,
                                                       }
                    id_mail = self.pool.get('mail.mail').create(cr,uid,data_mail)
                    print "data mail"
                    print data_mail
                    print "id_mail"
                    print id_mail
                    result=self.pool.get('mail.mail').send(cr,uid,[id_mail])
                    print "mail envoyé"
                    print result
        return True
    
    def envoyer_mail_annule(self,cr,uid,ids,context={}):
        print "fonction envoi mail"
        for objet_travail in self.browse(cr,uid,ids):
            if objet_travail.state == 'draft':
                if objet_travail.executeur_id and objet_travail.executeur_id.email:
                    data_text = u"""<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
                    
                     <p>Bonjour %s,</p>
                     
                     <p>Le travail de référence %s pour le dossier %s, demandé par %s à la date du %s a été annulé. </p>
                     <p>Il concernait la description suivante : </p>
                     <p>%s</p>
                     """ %(objet_travail.executeur_id.name, objet_travail.name, objet_travail.dossier_id and objet_travail.dossier_id.name, objet_travail.demandeur_id.name,objet_travail.date_demande,objet_travail.libelle_travail.name)
                    data_mail={
                                                       'type' : 'email',
                                                       'subject' : u'Annulation de travail',
                                                       'date' : time.strftime('%Y-%m-%d %H:%M:%S'),
                                                       'email_to' : objet_travail.executeur_id.email,
                                                       'body_html' : data_text,
                                                       }
                    id_mail = self.pool.get('mail.mail').create(cr,uid,data_mail)
                    result=self.pool.get('mail.mail').send(cr,uid,[id_mail])
        return True
    
    
    def envoyer_mail_execute(self,cr,uid,ids,context={}):
        print "fonction envoi mail"
        for objet_travail in self.browse(cr,uid,ids):
            if objet_travail.state == 'envoye':
                if objet_travail.demandeur_id and objet_travail.demandeur_id.email:
                    data_text = u"""<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
                    
                     <p>Bonjour %s,</p>
                     
                     <p>Le travail de référence %s, pour le dossier %s attribué à %s, a été achevé à la date du %s </p>
                     <p>Il concernait la description suivante : </p>
                     <p>%s</p>
                     """ %(objet_travail.demandeur_id.name, objet_travail.name, objet_travail.dossier_id and objet_travail.dossier_id.name, objet_travail.executeur_id.name,objet_travail.date_demande,objet_travail.libelle_travail.name)
                    data_mail={
                                                       'type' : 'email',
                                                       'subject' : u'Fin de travail',
                                                       'date' : time.strftime('%Y-%m-%d %H:%M:%S'),
                                                       'email_to' : objet_travail.demandeur_id.email,
                                                       'body_html' : data_text,
                                                       }
                    id_mail = self.pool.get('mail.mail').create(cr,uid,data_mail)
                    result=self.pool.get('mail.mail').send(cr,uid,[id_mail])
        return True

    _defaults = {
        'date_demande' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': '/',
        'state': lambda *a: 'draft',
    }

    _order = "date_demande desc"

    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'travail.effectue')
        return super(travail_effectue,self).create(cr, user, vals, context)


    def travail_effectue_cancel(self, cr, uid, ids, context=None):
        self.envoyer_mail_annule(cr,uid,ids)
        self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def travail_effectue_envoye(self, cr, uid, ids, context=None):
        self.envoyer_mail_demande(cr,uid,ids)
        return self.write(cr, uid, ids, {'state': 'envoye'}, context=None)


    def travail_effectue_execute(self, cr, uid, ids, context=None):
        self.envoyer_mail_execute(cr,uid,ids)
        self.write(cr, uid, ids, {'state': 'execute','date_realisation' : time.strftime('%Y-%m-%d %H:%M:%S') }, context=None)


    def travail_effectue_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)

travail_effectue()


#### LIBELLE TRAVAIL ###########################"

class libelle_travail(osv.osv):
    _name = 'libelle.travail'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['code','name'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = name +' ('+record['code']+')'
            res.append((record['id'], name))
        return res


    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)


    _columns = {

        'code' : fields.char(u'Code libellé travail',size=50, required=True),
        'name' : fields.char(u'Nom libellé travail',size=50, required=True),

    }
libelle_travail()

######## Rayon ###################################################################
class notariat_rayon(osv.osv):
    _name = 'notariat.rayon'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['code','name'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = name +' ('+record['code']+')'
            res.append((record['id'], name))
        return res


    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)


    _columns = {

        'code' : fields.char(u'Code rayon',size=50, required=True),
        'name' : fields.char(u'Nom rayon',size=50, required=True),
        'rayonnages_id': fields.one2many('notariat.rayonnage', 'rayon_id', u'Rayonnages liés'),

    }



    _sql_constraints = [('name_uniq','unique(name)', 'NOM RAYON DOIT ETRE UNIQUE!'),('code_uniq','unique(code)', 'CODE RAYON DOIT ETRE UNIQUE!')]
notariat_rayon()


#### Type affaire #######################################################################################
class notariat_affaire(osv.osv):
    _name = 'notariat.affaire'
    _columns = {

        'code': fields.char(u'Code affaire', size=64, required=True),
        'name': fields.char(u'Nom affaire', size=64, required=True),
        'ligne_affaire_id': fields.one2many('ligne.affaire', 'type_affaire_id', u'Parties'),




    }


    _sql_constraints = [('code_uniq','unique(code)', 'LE CODE DOIT ETRE UNIQUE!'),('name_uniq','unique(name)', 'LE NOM DOIT ETRE UNIQUE!')]

notariat_affaire()


#### LIGNE Type affaire #######################################################################################
class ligne_affaire(osv.osv):
    _name = 'ligne.affaire'
    _columns = {

        'partie_id' : fields.many2one('notariat.partie',u'Partie'),
        'nom_partie':fields.char(u'Intitule partie',size=100),
        'type_affaire_id': fields.many2one('notariat.affaire', u'Type affaire', ondelete='cascade', select=True),
    }


    def onchange_ligne_affaire_id(self, cr, uid, ids, partie_id):
        partie = self.pool.get('notariat.partie').browse(cr, uid, partie_id)
        if partie:
            result = {'value': {
                                'nom_partie' :   partie.nom_partie,
                                }
                        }

        return result
    


ligne_affaire()

######## Unite de mesure ###################################################################
class notariat_unite(osv.osv):
    _name = 'notariat.unite'
    _columns = {

        'code' : fields.char(u'Code unité',size=50),
        'name' : fields.char(u'Nom unité',size=50),
}

    _sql_constraints = [('code_uniq','unique(code)', 'CODE DOIT ETRE UNIQUE!'),('name_uniq','unique(name)', 'LE NOM DOIT ETRE UNIQUE!')] 





notariat_unite()

######## ville ################################################################################



class notariat_ville(osv.osv):
    _name = 'notariat.ville'


    def _get_country(self, cr, uid, context):
        country_obj = self.pool.get('res.country')
        res = country_obj.search(cr, uid, [('code', '=', 'MA')], limit=1)
        if res:
            return res[0]
        else:
            return False


    _columns = {

        'name' : fields.char(u'المدينة',size=50),
        'name_ville' : fields.char(u'Nom ville',size=50),
        'pays_id' : fields.many2one('res.country',u'Pays', ondelete='cascade'),
}


    _defaults = {


        'pays_id' :_get_country,



    }

notariat_ville()

########### Partie ##################################################################
class notariat_partie(osv.osv):
    _name="notariat.partie"


    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['code_partie','name'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code_partie']:
                name = name +' ('+record['code_partie']+')'
            res.append((record['id'], name))
        return res


    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    _columns={
        'name':fields.selection([('PARTIE 1', u'PARTIE 1'), ('PARTIE 2', u'PARTIE 2'),('PARTIE 3', u'PARTIE 3')], u'Intitulé'),
        'nom_partie':fields.char(u'Nom partie',size=100),
        'code_partie':fields.char(u'Code partie',size=100),



    }   



notariat_partie()

####### Rayonnage dossiers ###################################################################
class notariat_rayonnage(osv.osv):
    _name = 'notariat.rayonnage'



    def _get_repertoire_name(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.dossier_id.name_repertoire
        return res 


    _columns = {

        'date_rayonnage' : fields.datetime(u'Date rayonnage'),
        'rayon_id' : fields.many2one('notariat.rayon',u'Rayon', required=True),
        'user_id' : fields.many2one('res.users',u'Utilisateur'),
        'dossier_id' : fields.many2one('notariat.dossier',u'Dossier'),
        'observation' : fields.text(u'Observations'),
        'repertoire_name': fields.function(_get_repertoire_name, method=True, type='char', string=u'Répertoire'),



    }
    _defaults = {


        'date_rayonnage' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda object,cr,uid,context: uid,
        #'dossier_id': lambda self, cr, uid, context: self.pool.get('notariat.dossier'),
    }



notariat_rayonnage()

######### Lieu conservation #####################################



class lieu_conservation(osv.osv):
    _name="lieu.conservation"
    _columns={
        'name':fields.char(u'District',size=50),
        'region':fields.char(u'Région',size=50),
        'ville_id':fields.many2one('notariat.ville',u'Ville', required=True),

    }    

lieu_conservation()



########### BIEN ############################################################

class notariat_bien(osv.osv):
    _name = 'notariat.bien'
    _inherit = ['mail.thread']


    def _get_country(self, cr, uid, context):
        country_obj = self.pool.get('res.country')
        res = country_obj.search(cr, uid, [('code', '=', 'MA')], limit=1)
        if res:
            return res[0]
        else:
            return False


    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['numero_ordre','indice'], context=context)
        res = []
        for record in reads:
            name = record['numero_ordre']
            if record['indice']:
                name = str(record['numero_ordre'])+'/'+record['indice']
            res.append((record['id'], name))
        return res


    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)


    def _get_last_dossier(self, cr, uid, ids, name, args, context):
        res = {}
        obj_doss = self.pool.get('notariat.dossier')
        for bien in self.browse(cr, uid, ids, context=context):
            doss_ids = obj_doss.search(cr, uid, [('biens_ids','=',bien.id),], order='date_creation_dossier', context=context)
            if doss_ids:
                res[bien.id] = doss_ids[-1:][0]
                res[bien.id] = obj_doss.browse(cr, uid, doss_ids[-1:][0], context=context).name
            else:
                res[bien.id] = False
        return res



    def attachment_tree_view_bien(self, cr, uid, ids, context):
        rep_ids = self.pool.get('consultation.bien').search(cr, uid, [('bien_id', 'in', ids)])
        domain = [
             '|', 
             '&', ('res_model', '=', 'notariat.bien'), ('res_id', 'in', ids),
             '&', ('res_model', '=', 'consultation.bien'), ('res_id', 'in', rep_ids)
		]
        res_id = ids and ids[0] or False
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }





    _columns = {

        'name' : fields.function(_name_get_fnc, type="char", string=u'N° Titre foncier'),
        'numero_ordre' : fields.char(u'N° Ordre',size=50),
        'indice' : fields.char(u'Indice',size=50),
        'designation' : fields.many2one('designation.bien',u'Désignation Bien',required=True),
        'adresse' : fields.char(u'Adresse',size=50),
        'ville' : fields.many2one('notariat.ville',u'Ville', required=True),
        'pays' : fields.many2one('res.country',u'Pays', required=True),
        'description' : fields.char(u'Description',size=50),
        'numero_lot' : fields.char(u'Numero de lôt',size=50),
        'etage' : fields.char(u'Etage',size=50),
        'superficie':fields.char(u'superficie',size=10),
	    'unite': fields.many2one('notariat.unite',u'Unite de mesure'),
        'numero_tf_mere' : fields.char(u'Numero T.F. Mère',size=50),
        'millieme' : fields.char(u'millieme',size=50),
        'fraction' : fields.char(u'Fraction',size=50),
        'acquis_le' : fields.date(u'Acquis le'),
        'enregistre_le' : fields.date(u'Enregistré le'),
        'reference' : fields.char(u'S References',size=50, help=u'Réference chèque de l\'enregistrement'),
        'dv_enregistrement': fields.char(u'DV',size=200),
        'or_enregistrement': fields.char(u'OR',size=200),
        're_enregistrement': fields.char(u'RE',size=200),
        'e17b_enregistrement': fields.char(u'E17B',size=200),

	    'lieu_conservation': fields.many2one('lieu.conservation',u'Lieu conservation', required=True, help=u"Lieu de conservation"),

        'type_acte_id': fields.many2one('type.acte',u'Type acte'),
	    'user_id': fields.many2one('res.users',u'Utilisateur'),
        'proprietes_id': fields.one2many('proprietaire.bien', 'bien_id', u'Propriétés liés'),
        'consultations_id': fields.one2many('consultation.bien', 'bien_id', u'Consultations liés'),
        'dossiers_ids': fields.many2many('notariat.dossier', 'doss_bien_rel', 'bien_id', 'dossier_id', 'Dossiers'),
        'last_dossier': fields.function(_get_last_dossier, method=True, type='char', string=u'Dernier dossier'),



    }

    _sql_constraints = [('titre_foncier_uniq','unique(numero_ordre,indice)', 'TITRE FONCIER DOIT ETRE UNIQUE!')] 

    _defaults = {

        'user_id': lambda object,cr,uid,context: uid,
        'pays' :_get_country,
        'etage' : 0,



    }



notariat_bien()


######## TYPE ACTE BIEN ###################################################################
class type_acte(osv.osv):
    _name = 'type.acte'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['code','name'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = name +' ('+record['code']+')'
            res.append((record['id'], name))
        return res


    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)


    _columns = {

        'code' : fields.char(u'Code acte',size=50, required=True),
        'name' : fields.char(u'Nom acte',size=50, required=True),

    }
type_acte()



######## DOSSIER ########################################################################
class notariat_dossier(osv.osv):
    _name = 'notariat.dossier'







    def attachment_tree_view(self, cr, uid, ids, context):
        rep_ids = self.pool.get('notariat.repertoire').search(cr, uid, [('dossier_id', 'in', ids)])
        domain = [
             '|', 
             '&', ('res_model', '=', 'notariat.dossier'), ('res_id', 'in', ids),
             '&', ('res_model', '=', 'notariat.repertoire'), ('res_id', 'in', rep_ids)
		]
        res_id = ids and ids[0] or False
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }


##  TITRE FONCIERS DES BIENS DANS LE DOSSIER TREE


    def _get_tf_many(self, cr, uid, ids, name, args, context):
        res = {}
        for doss in self.browse(cr, uid, ids, context=context):
            objets = []
            for obj in doss.biens_ids:
                objets.append((obj.name).encode("utf-8")+"\n"+"\n")
                res[doss.id] = ''.join(objets)
            return res




##  LOT  DES BIENS DANS LE DOSSIER TREE

    def _get_lot_many(self, cr, uid, ids, name, args, context):
        res = {}
        for doss in self.browse(cr, uid, ids, context=context):
            objets = []
            for obj in doss.biens_ids:
                objets.append((obj.numero_lot).encode("utf-8")+"\n"+"\n")
                res[doss.id] = ''.join(objets)
            return res





##  LIEU CONSERVATION DES BIENS DANS LE DOSSIER TREE


    def _get_lieu_many(self, cr, uid, ids, name, args, context):
        res = {}
        for doss in self.browse(cr, uid, ids, context=context):
            objets = []
            for obj in doss.biens_ids:
                objets.append((obj.lieu_conservation.name).encode("utf-8")+"\n"+"\n")
                res[doss.id] = ''.join(objets)
            return res




##  ETAGE DES BIENS DANS LE DOSSIER TREE


    def _get_lieu_etage(self, cr, uid, ids, name, args, context):
        res = {}
        for doss in self.browse(cr, uid, ids, context=context):
            objets = []
            for obj in doss.biens_ids:
                objets.append((obj.etage).encode("utf-8")+"\n"+"\n")
                res[doss.id] = ''.join(objets)
            return res






### PARTIE 1 DANS LA LISTE DES DOSSIERS 
    def _get_partie1(self, cr, uid, ids, name, args, context):
        res = {}
        obj_partie = self.pool.get('dossier.partie')
        obj_client = self.pool.get('partie.client')
        for doss in self.browse(cr, uid, ids, context=context):
            partie_ids = obj_partie.search(cr, uid, [('dossier_id','=',doss.id),('partie_id','=','PARTIE 1')], context=context)
            if partie_ids :
                for partie in partie_ids :
                    client_ids = obj_client.search(cr, uid, [('ligne_partie_id','=',partie)], context=context)
                    #print client_ids
                    if client_ids :
                        customers = []
                        n = 1
                        for ci in client_ids :
                            customers.append(str(n)+"-"+obj_client.browse(cr, uid, ci, context=context).customer_id.complete_name+"\n"+"\n")
                            n = n + 1 
                            res[doss.id] = ''.join(customers)
                    else : 
                        res[doss.id] = False
            else :
                    res[doss.id] = False
        return res



### PARTIE 2 DANS LA LISTE DES DOSSIERS 
    def _get_partie2(self, cr, uid, ids, name, args, context):
        res = {}
        obj_partie = self.pool.get('dossier.partie')
        obj_client = self.pool.get('partie.client')
        for doss in self.browse(cr, uid, ids, context=context):
            partie_ids = obj_partie.search(cr, uid, [('dossier_id','=',doss.id),('partie_id','=','PARTIE 2')], context=context)
            if partie_ids :
                for partie in partie_ids :
                    client_ids = obj_client.search(cr, uid, [('ligne_partie_id','=',partie)], context=context)
                    #print client_ids
                    if client_ids :
                        customers = []
                        n = 1
                        for ci in client_ids :
                            customers.append(str(n)+"-"+obj_client.browse(cr, uid, ci, context=context).customer_id.complete_name+"\n"+"\n")
                            n = n + 1 
                            res[doss.id] = ''.join(customers)
                    else : 
                        res[doss.id] = False
            else :
                    res[doss.id] = False
        return res



### PARTIE 3 DANS LA LISTE DES DOSSIERS 
    def _get_partie3(self, cr, uid, ids, name, args, context):
        res = {}
        obj_partie = self.pool.get('dossier.partie')
        obj_client = self.pool.get('partie.client')
        for doss in self.browse(cr, uid, ids, context=context):
            partie_ids = obj_partie.search(cr, uid, [('dossier_id','=',doss.id),('partie_id','=','PARTIE 3')], context=context)
            if partie_ids :
                for partie in partie_ids :
                    client_ids = obj_client.search(cr, uid, [('ligne_partie_id','=',partie)], context=context)
                    #print client_ids
                    if client_ids :
                        customers = []
                        n = 1
                        for ci in client_ids :
                            customers.append(str(n)+"-"+obj_client.browse(cr, uid, ci, context=context).customer_id.complete_name+"\n"+"\n")
                            n = n + 1 
                            res[doss.id] = ''.join(customers)
                    else : 
                        res[doss.id] = False
            else :
                    res[doss.id] = False
        return res


## DERNIER UTILISATEUR QUI A MODIFIE LE DOSSIER
    def _get_dernier_utilisateur(self, cr, uid, ids, name, args, context):
        res = {}
        obj_audit = self.pool.get('auditlog.log')
        for doss in self.browse(cr, uid, ids, context=context):
            audit_ids = obj_audit.search(cr, uid, [('name','=',doss.name),], order='create_date', context=context)
            if audit_ids:
                res[doss.id] = audit_ids[-1:][0]
                res[doss.id] = obj_audit.browse(cr, uid, audit_ids[-1:][0], context=context).user_id.name
            else:
                res[doss.id] = False
        return res


## DERNIERE DATE DE MODIFICATION
    def _get_dernier_date_modification(self, cr, uid, ids, name, args, context):
        res = {}
        obj_audit = self.pool.get('auditlog.log')
        for doss in self.browse(cr, uid, ids, context=context):
            audit_ids = obj_audit.search(cr, uid, [('name','=',doss.name),], order='create_date', context=context)
            if audit_ids:
                res[doss.id] = audit_ids[-1:][0]
                res[doss.id] = obj_audit.browse(cr, uid, audit_ids[-1:][0], context=context).create_date
            else:
                res[doss.id] = False
        return res



    _columns = {
        'name' : fields.char(u'Numéro dossier',size=50, readonly=True),
        'name_repertoire' : fields.char(u'N° Répertoires',size=150),
        'date_creation_dossier' : fields.datetime(u'Date création dossier',readonly=True),
        'date_cloture_dossier' : fields.datetime(u'Date cloture dossier'),
        'observation':fields.text(u'Observations'),
        'type_affaire_id' : fields.many2one('notariat.affaire',u'Type affaire'),
        'designation' : fields.char(u'Désignation',size=50),
        'montant_transaction':fields.float(u'Mont. transaction'),
        'montant_vue':fields.float(u'Mont./Vue notaire'),
        'rayon_id' : fields.many2one('notariat.rayon',u'Rayon'),
        'user_id' : fields.many2one('res.users',u'Utilisateur'),
        'montant_id': fields.one2many('notariat.montant', 'dossier_id', u'Montants'),
        'partie_id': fields.one2many('dossier.partie', 'dossier_id', u'Intitlé Partie'),
        'repertoire_id': fields.one2many('notariat.repertoire', 'dossier_id', u'Répertoires'),
        'state':fields.selection([('prepare', u'En préparation'),('draft', u'Brouillon'), ('Valide', u'Répertorié'),('cancel', u'Annulé'),('cloture', u'Cloturé'),], 'Etat Dossier'),
        'dernier_utilisateur': fields.function(_get_dernier_utilisateur, method=True, type='char', string=u'Dernier utilisateur'),
        'dernier_date_modification': fields.function(_get_dernier_date_modification, method=True, type='datetime', string=u'Dernier date modification'),
        'partie1': fields.function(_get_partie1, method=True, type='char', string=u'Partie 1', store=True),
        'partie2': fields.function(_get_partie2, method=True, type='char', string=u'Partie 2', store=True),
        'partie3': fields.function(_get_partie3, method=True, type='char', string=u'Partie 3', store=True),
        'biens_ids': fields.many2many('notariat.bien', 'doss_bien_rel', 'dossier_id', 'bien_id', 'Biens'),
        'tf_objet': fields.function(_get_tf_many, method=True, type='char', string=u'TF', store=True),
        'lot_objet': fields.function(_get_lot_many, method=True, type='char', string=u'Lot', store=True),
        'lieu_objet': fields.function(_get_lieu_many, method=True, type='char', string=u'Lieu CF', store=True),
        'etage_objet': fields.function(_get_tf_many, method=True, type='char', string=u'Etage', store=True),
        'prepa_consultation_ok': fields.boolean(u'Consultation?'),
        'executeur_prepa_consultation' : fields.many2one('res.users',u'Exec. Consultation'),
        'prepa_certification_ok': fields.boolean(u'certificat.?'),
        'executeur_prepa_certification' : fields.many2one('res.users',u'Exec. certificat.'),
        'prepa_complement_ok': fields.boolean(u'Demande de complément enregistrement?'),
        'executeur_prepa_complement' : fields.many2one('res.users',u'Exec. complément enregistrement'),
        'prepa_mletat_ok': fields.boolean(u'ML Etat?'),
        'executeur_prepa_mletat' : fields.many2one('res.users',u'Exec. ML Etat'),
        'prepa_mlbanque_ok': fields.boolean(u'ML Banque?'),
        'executeur_prepa_mlbanque' : fields.many2one('res.users',u'Exec. ML Banque'),
        'prepa_certifnegatif_ok': fields.boolean(u'Certification Négatif?'),
        'executeur_prepa_certifnegatif' : fields.many2one('res.users',u'Exec. Certification Négatif'),
        'prepa_copieachat_ok': fields.boolean(u'Copie contrat achat?'),
        'executeur_prepa_copieachat' : fields.many2one('res.users',u'Exec. Copie contrat achat'),
        'prepa_origineprop_ok': fields.boolean(u'Origine de propriété?'),
        'executeur_prepa_origineprop' : fields.many2one('res.users',u'Exec. Origine de propriété'),
        'prepa_demande_decompte_ok': fields.boolean(u'Demande de décompte?'),
        'executeur_prepa_demande_decompte' : fields.many2one('res.users',u'Exec. Demande de décompte'),
        'prepa_plan_topogra_ok': fields.boolean(u'Plan topographique?'),
        'executeur_prepa_plan_topogra' : fields.many2one('res.users',u'Exec. Plan topographique'),
        'prepa_note_rens_ok': fields.boolean(u'Note de renseignement?'),
        'executeur_prepa_note_rens' : fields.many2one('res.users',u'Exec. Note de renseignement'),
        'prepa_patente_ok': fields.boolean(u'Patente?'),
        'executeur_prepa_patente' : fields.many2one('res.users',u'Exec. Patente'),
        'prepa_rc_ok': fields.boolean(u'RC?'),
        'executeur_prepa_rc' : fields.many2one('res.users',u'Exec. RC'),
        'prepa_bulletin_officiel_ok': fields.boolean(u'Bulletin officiel?'),
        'executeur_prepa_bulletin_officiel' : fields.many2one('res.users',u'Exec. Bulletion officiel'),
        'prepa_journal_local_ok': fields.boolean(u'Journal local?'),
        'executeur_prepa_journal_local' : fields.many2one('res.users',u'Exec. Journal Local'),
        'prepa_cnss_ok': fields.boolean(u'CNSS?'),
        'executeur_prepa_cnss' : fields.many2one('res.users',u'Exec. CNSS'),
        'prepa_autre_ok': fields.boolean(u'Autre?'),
        'executeur_prepa_autre' : fields.many2one('res.users',u'Exec. Autre'),
        'observations_autre' : fields.char(u'Observations Autre',size=50),
        'visites_id': fields.one2many('visite.client', 'dossier_id', u'Visites liées'),
        'travaux_id': fields.one2many('travail.effectue', 'dossier_id', u'Travaux liés'),
        'entrants_id': fields.one2many('appel.entrant', 'dossier_id', u'Appels entrants'),
        'sortants_id': fields.one2many('appel.sortant', 'dossier_id', u'Appels sortants'),
        'rayonnages_id': fields.one2many('notariat.rayonnage', 'dossier_id', u'Rayonnages liées'),
    }


    _defaults = {

        'date_creation_dossier' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda object,cr,uid,context: uid,
        'state': lambda *a: 'draft',
        'name': '/',
    }


    _order = "name desc"



    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'notariat.dossier')
        return super(notariat_dossier,self).create(cr, user, vals, context)




    def onchange_type_affaire(self,cr, uid, ids, type_affaire_id=False, context=None):
        sp_ids = self.pool.get('ligne.affaire').search(cr, uid,[('type_affaire_id','=', type_affaire_id)])
        print sp_ids
        for sp in sp_ids :
            result = {'value': {'partie_id' : [{'nom_partie': self.pool.get('ligne.affaire').browse(cr, uid, sp).nom_partie, 'partie_id': self.pool.get('ligne.affaire').browse(cr, uid, sp).partie_id.id,} for sp in sp_ids]}}
            return result




    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer que les dossiers Brouillon !'))
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)




    def dos_preparer(self, cr, uid, ids, context=None):
        doss = self.browse(cr, uid, ids)[0]
        if doss.prepa_consultation_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'POUR CONSULTATION')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_consultation.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_certification_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'POUR CERTIFICAT DE PROPRIETE')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_certification.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_complement_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'DEMANDE COMPLÉMENT ENREGISTREMENT')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_complement.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_mletat_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'ML ETAT')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_mletat.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_mlbanque_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'ML BANQUE')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_mlbanque.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_certifnegatif_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'CERTIFICATION NEGATIF')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_certifnegatif.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_copieachat_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'COPIE CONTRAT ACHAT')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_copieachat.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_origineprop_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'ORIGINE PROPRIETE')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids  
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_origineprop.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_demande_decompte_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'DEMANDE DE DÉCOMPTE')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_demande_decompte.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_plan_topogra_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'PLAN TOPOPGRAPHIQUE')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_plan_topogra.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_note_rens_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'NOTE DE RENSEIGNEMENT')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_note_rens.id,
				'libelle_travail': libe.id,

				})

        if doss.prepa_patente_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'PATENTE')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_patente.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_rc_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'RC')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]   
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_rc.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_bulletin_officiel_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'BULLETIN OFFICIEL')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_bulletin_officiel.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_journal_local_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'JOURNAL LOCAL')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_journal_local.id,
				'libelle_travail': libe.id,

				})

        if doss.prepa_cnss_ok:
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'CNSS')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_cnss.id,
				'libelle_travail': libe.id,

				})
        if doss.prepa_autre_ok :
            libe_ids  = self.pool.get('libelle.travail').search(cr, uid, [('name', '=', 'AUTRE')], limit=1)
            libe = self.pool.get('libelle.travail').browse(cr, uid, libe_ids, context=context)[0]
            print libe_ids
            pr_id = self.pool.get('travail.effectue').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'travail.effectue'),
				'dossier_id': doss.id,
				'date_demande': time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id': doss.user_id.id,
				'executeur_id': doss.executeur_prepa_autre.id,
				'libelle_travail': libe.id,
				'observation': doss.observations_autre,

				})



        return self.write(cr, uid, ids, {'state': 'prepare'}, context=None)


    def dos_valide(self, cr, uid, ids, context=None, *args):
        name_repertoire_dossier = ''
        dos_id = self.browse(cr, uid, ids)[0]
        for line in self.browse(cr, uid, ids):
            if not line.repertoire_id :
                raise osv.except_osv(_('Action non valide  !'), _('PAS DE REPERTOIRES DANS LE DOSSIER!'))
        for line in self.browse(cr, uid, ids):
            if not line.biens_ids :
                raise osv.except_osv(_('Action non valide  !'), _('PAS DE BIENS DANS LE DOSSIER!'))
        for line in dos_id.repertoire_id:
            if line['state'] not in ['repertorie'] :
                raise osv.except_osv(_('Action non valide  !'), _('VOUS NE POUVEZ PAS RÉPERTORIER UN DOSSIER AVEC DES CONTRATS NON ENCORE RÉPERTORIES!'))
            name_repertoire_dossier += '('+line.name+')'+' '			
        return self.write(cr, uid, ids, {'state': 'Valide', 'name_repertoire':name_repertoire_dossier}, context=None)



    def dos_cancel(self, cr, uid, ids, context=None):
        dos_id = self.browse(cr, uid, ids)[0]
        for line in dos_id.repertoire_id:
            if line['state'] != 'cancel' :
                raise osv.except_osv(_('Action non valide  !'), _(u'VOUS NE POUVEZ PAS Annuler UN DOSSIER AVEC DES REPERTOIRES NON ENCORE Annulés!'))
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def dos_cloture(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cloture'}, context=None)


    def dos_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)





notariat_dossier()

#### LIGNE DOSSIER PARTIE  ###########################################################################

class dossier_partie(osv.osv):
    _name = 'dossier.partie'





    def _somme_quote(self, cr, uid, ids):
        for partie in self.browse(cr, uid, ids) :
            #print partie
            client_ids = self.pool.get('partie.client').search(cr, uid,[ ('ligne_partie_id', '=', partie.id), ])
            #print client_ids
            if client_ids :
                somme_quote = 0/1
                for ci in client_ids:
                    somme_quote += Fraction(self.pool.get('partie.client').browse(cr, uid, ci).quote)
                    #print somme_quote
                if somme_quote != 1 :
                    return False
                return True
            else  :
                return True


    def _zero_quote(self, cr, uid, ids):
        for partie in self.browse(cr, uid, ids) :
            #print partie
            client_ids = self.pool.get('partie.client').search(cr, uid,[ ('ligne_partie_id', '=', partie.id), ])
            print client_ids
            if client_ids :
                quote = 0/1
                for ci in client_ids:
                    quote = Fraction(self.pool.get('partie.client').browse(cr, uid, ci).quote)
                    if quote == 0 :
                        return False
                return True
            else :
                return True
        

    def _get_partie_client(self, cr, uid, ids, name, args, context):
        res = {}
        obj_partie = self.pool.get('dossier.partie')
        obj_client = self.pool.get('partie.client')
        customers = []
        for partie in self.browse(cr, uid, ids, context=context):
            clients_ids = obj_client.search(cr, uid, [('ligne_partie_id','=',partie.id)], context=context)
            n = 1
            for client in clients_ids :
                    if clients_ids :
                        customers.append(str(n)+"-"+obj_client.browse(cr, uid, client, context=context).customer_id.complete_name+"\n"+"\n")
                        n = n + 1 
                        res[partie.id] = ''.join(customers)
                    else : 
                        res[partie.id] = False

            return res   


    def _get_partie_client_quote(self, cr, uid, ids, name, args, context):
        res = {}
        obj_partie = self.pool.get('dossier.partie')
        obj_client = self.pool.get('partie.client')
        customers = []
        for partie in self.browse(cr, uid, ids, context=context):
            clients_ids = obj_client.search(cr, uid, [('ligne_partie_id','=',partie.id)], context=context)
            for client in clients_ids :
                    if clients_ids :
                        customers.append(obj_client.browse(cr, uid, client, context=context).quote+"\n"+"\n")
                        res[partie.id] = ''.join(customers)
                    else : 
                        res[partie.id] = False

            return res   


    def _get_partie_client_qualite(self, cr, uid, ids, name, args, context):
        res = {}
        obj_partie = self.pool.get('dossier.partie')
        obj_client = self.pool.get('partie.client')
        customers = []
        for partie in self.browse(cr, uid, ids, context=context):
            clients_ids = obj_client.search(cr, uid, [('ligne_partie_id','=',partie.id)], context=context)
            for client in clients_ids :
                    if clients_ids :
                        customers.append(obj_client.browse(cr, uid, client, context=context).qualite+"\n"+"\n")
                        res[partie.id] = ''.join(customers)
                    else : 
                        res[partie.id] = False

            return res          


    _columns = {

        'partie_id' : fields.many2one('notariat.partie',u'Partie'),
        'nom_partie':fields.char(u'Nom partie',size=100),
        'dossier_id' : fields.many2one('notariat.dossier',u'Dossier'),
        'partie_client_id': fields.one2many('partie.client', 'ligne_partie_id', u'Clients'),
        'client_liste': fields.function(_get_partie_client, method=True, type='char', string=u'Clients', store=True),
        'client_quote': fields.function(_get_partie_client_quote, method=True, type='char', string=u'Quotes', store=True),
        'client_qualite': fields.function(_get_partie_client_qualite, method=True, type='char', string=u'Qualité', store=True),




    }

    def onchange_dossier_partie_id(self, cr, uid, ids, partie_id):
        partie = self.pool.get('notariat.partie').browse(cr, uid, partie_id)
        result = {'value': {
                            'nom_partie' :   partie.nom_partie,

                            }

                    }

        return result



    _constraints = [(_somme_quote,'Somme quote doit Egale 1 !', ['quote']),(_zero_quote,'Quote doit ETRE SUP A ZERO!', ['quote'])]

dossier_partie()

#### LIGNE PARTIE CLIENT  ###########################################################################

class partie_client(osv.osv):
    _name = 'partie.client'



    _columns = {


        'ligne_partie_id' : fields.many2one('dossier.partie',u'Partie'),
        'customer_id':fields.many2one('res.partner',u'Client'),
        'quote': fields.char('Quote', size=64),
        'qualite':fields.selection([('agiss', u'Agissant pour leur compte'), ('autrui', u'Compte d\'autrui'),('represente', u'Represente'),], u'Qualité'),
       

    }



    _sql_constraints = [('name_uniq','unique(customer_id,ligne_partie_id)', 'CLIENT DOIT ETRE UNIQUE POUR LA MEME PARTIE!')]




dossier_partie()



#### MONTANT ###########################################################################



class notariat_montant(osv.osv):
    _name = 'notariat.montant'
    _columns = {

        'observation' : fields.char(u'Observation sur le montant',size=50),
        'montant':fields.float(u'Montant'),
        'type_montant' : fields.many2one('type.montant',u'Type paiement prix',required=True),
        'dossier_id': fields.many2one('notariat.dossier', 'Ref dossier', select=True),

    }


notariat_montant()

##########  REPERTOIRE ##################################
class type_repertoire(osv.osv):
    _name = 'type.repertoire'
    _columns = {

        'name' : fields.char(u'Libellé répertoire',size=50),
        'enregistrement_ok': fields.boolean(u'Enreg?'),
        'type_enregistrement' : fields.selection([('taux',u'Taux'),('fixe',u'Fixe')],u'Type montant enreg.'),
        'taux_enregistrement':fields.float(u'Taux enreg'),
        'fixe_enregistrement':fields.float(u'Fixe enreg'),
        'delai_enregistrement':fields.integer(u'Délai enregistrement'),
        'conservation_ok': fields.boolean(u'CF?'),
        'delai_conservation':fields.integer(u'Délai CF'),
        'type_conservation' : fields.selection([('taux',u'Taux'),('fixe',u'Fixe')],u'Type montant cons.'),
        'taux_cons':fields.float(u'Taux cons'),
        'fixe_cons':fields.float(u'Fixe cons'),
        'certification_ok': fields.boolean(u'Certificat. de propriété?'),
        'executeur_certificat_id': fields.many2one('res.users', 'Exécuteur Certificat de propriété'),
        'banque_ok': fields.boolean('Banque?'),
        'impot_tpi_ok': fields.boolean(u'Impôt TPI?'),
        'delai_tpi':fields.integer(u'Délai TPI'),
        'impot_te_ok': fields.boolean(u'Impôt TE?'),
        'delai_te':fields.integer(u'Délai TE'),
        'impot_tnb_ok': fields.boolean(u'Impôt TNB?'),
        'delai_tnb':fields.integer(u'Délai TNB'),
        'quitus_ok': fields.boolean(u'Quitus?'),


    }


    _sql_constraints = [('name_uniq','unique(name)', 'LIBELLE TYPE REPERTOIRE DOIT ETRE UNIQUE!')]



type_repertoire()

##########  REPERTOIRE ##################################
class notariat_repertoire(osv.osv):
    _inherit = ['mail.thread']
    _name = 'notariat.repertoire'


    def _get_partie1(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.dossier_id.partie1
        return res 


    def _get_partie2(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.dossier_id.partie2
        return res 


    def _get_partie3(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.dossier_id.partie3
        return res 



    def _get_tf(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.dossier_id.tf_objet
        return res 

    def _get_lieu(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.dossier_id.lieu_objet
        return res 


    def _get_lot(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.dossier_id.lot_objet
        return res 





    def attachment_tree_view(self, cr, uid, ids, context):
        domain = [('res_model', '=', 'notariat.repertoire'), ('res_id', 'in', ids)]
        res_id = ids and ids[0] or False
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }






    _columns = {
        'code' : fields.char(u'Code informatique',size=50,readonly=True),
        'name' : fields.char(u'N° Rép',size=50),
        'libelle_id': fields.many2one('type.repertoire', u'Intitulé', select=True),
        'enregistrement_ok': fields.boolean(u'Enreg?'),
        'type_enregistrement' : fields.selection([('taux',u'Taux'),('fixe',u'Fixe')],u'Type montant enreg.'),
        'taux_enregistrement':fields.float(u'Taux enreg'),
        'fixe_enregistrement':fields.float(u'Fixe enreg'),
        'delai_enregistrement':fields.integer(u'Délai enregistrement'),
        'conservation_ok': fields.boolean(u'CF?'),
        'delai_conservation':fields.integer(u'Délai CF'),
        'type_conservation' : fields.selection([('taux',u'Taux'),('fixe',u'Fixe')],u'Type montant cons.'),
        'taux_cons':fields.float(u'Taux cons'),
        'fixe_cons':fields.float(u'Fixe cons'),
        'certification_ok': fields.boolean(u'CP?'),
        'executeur_certificat_id': fields.many2one('res.users', 'Exécuteur CP'),
        'banque_ok': fields.boolean('Banque?'),
        'impot_tpi_ok': fields.boolean(u'Impôt TPI?'),
        'type_tpi' : fields.selection([('client',u'Client'),('cabinet',u'Cabinet')],u'A la charge'),
        'delai_tpi':fields.integer(u'Délai TPI'),
        'impot_te_ok': fields.boolean(u'Impôt TE?'),
        'type_te' : fields.selection([('client',u'A la charge du client'),('cabinet',u'A la charge du cabinet')],u'A la charge'),
        'delai_te':fields.integer(u'Délai TE'),
        'impot_tnb_ok': fields.boolean(u'Impôt TNB?'),
        'type_tnb' : fields.selection([('client',u'A la charge du client'),('cabinet',u'A la charge du cabinet')],u'A la charge'),
        'delai_tnb':fields.integer(u'Délai TNB'),
        'quitus_ok': fields.boolean(u'Quitus?'),
        'dossier_id': fields.many2one('notariat.dossier', u'N° dossier', select=True),
        'user_id' : fields.many2one('res.users',u'Validé par'),
        'date_validation' : fields.datetime(u'Validé le'),
        'date_creation_repertoire' : fields.datetime(u'Date Création Rép'),
        'state':fields.selection([('draft', u'Brouillon'),('repertorie', u'Répertorié'),('valide', u'A Répértorier'),('cancel', u'Annulé')], u'Etat rép '),
        'partie1': fields.function(_get_partie1, method=True, type='char', string=u'Partie 1'),
        'partie2': fields.function(_get_partie2, method=True, type='char', string=u'Partie 2'),
        'partie3': fields.function(_get_partie3, method=True, type='char', string=u'Partie 3'),
        'lot_objet': fields.function(_get_lot, method=True, type='char', string=u'Lot'),
        'tf_objet': fields.function(_get_tf, method=True, type='char', string=u'TF'),
        'lieu_objet': fields.function(_get_lieu, method=True, type='char', string=u'Lieu CF'),
        'montant_repertoire':fields.float(u'Montant contrat'),
        'date_signature_repertoire' : fields.datetime(u'Date Signature'),




    }

    _order = "dossier_id desc"

    _defaults = {
		'name': lambda self, cr, uid, context: '/',
		'code': lambda self, cr, uid, context: '/',
		'state': lambda object,cr,uid,context: 'draft',
        	'date_creation_repertoire' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),


		}
    


    def onchange_type_repertoire_id(self, cr, uid, ids, libelle_id):
        result = {'value': {} }
        type_repertoire = self.pool.get('type.repertoire').browse(cr, uid, libelle_id)
        if type_repertoire:
            result = {'value': {
                                'enregistrement_ok' :   type_repertoire.enregistrement_ok,
                                'delai_enregistrement' :   type_repertoire.delai_enregistrement,
                                'type_enregistrement' :   type_repertoire.type_enregistrement,
                                'taux_enregistrement' :   type_repertoire.taux_enregistrement,
                                'fixe_enregistrement' :   type_repertoire.fixe_enregistrement,
                                'conservation_ok' :   type_repertoire.conservation_ok,
                                'delai_conservation' :   type_repertoire.delai_conservation,
                                'type_conservation' :   type_repertoire.type_conservation,
                                'taux_cons' :   type_repertoire.taux_cons,
                                'fixe_cons' :   type_repertoire.fixe_cons,
                                'certification_ok' :   type_repertoire.certification_ok,
                                'executeur_certificat_id' :   type_repertoire.executeur_certificat_id.id,
                                'banque_ok' :   type_repertoire.banque_ok,
                                'impot_tpi_ok' :   type_repertoire.impot_tpi_ok,
                                'delai_tpi' :   type_repertoire.delai_tpi,
                                'quitus_ok' :   type_repertoire.quitus_ok,
                                'impot_tnb_ok' :   type_repertoire.impot_tnb_ok,
                                'delai_tnb' :   type_repertoire.delai_tnb,
                                'impot_te_ok' :   type_repertoire.impot_te_ok,
                                'delai_te' :   type_repertoire.delai_te,
                                }
    
                        }

        return result


    def create(self, cr, user, vals, context=None):
        if ('dossier_id' not in vals):
            raise osv.except_osv(u'Procédure incorrecte !',u'Vous devez passer par un Dossier.')
        if ('code' not in vals) or (vals.get('code')=='/'):
            vals['code'] = self.pool.get('ir.sequence').get(cr, user, 'notariat.repertoire.code')
        return super(notariat_repertoire,self).create(cr, user, vals, context)



    def rep_cancel(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def rep_repertorie(self, cr, uid, ids, context=None):
		rep = self.browse(cr, uid, ids)[0]
		if rep.enregistrement_ok :
			pr_id = self.pool.get('notariat.enregistrement').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'notariat.enregistrement'),
				'state': 'draft',
				'repertoire_id': rep.id,
				'libelle': rep.libelle_id.name,
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,
				'date_demande_enregistrement': time.strftime('%Y-%m-%d %H:%M:%S'),
				'montant_systeme': float(rep.taux_enregistrement / 100) * float(rep.dossier_id.montant_transaction ) if rep.type_enregistrement == 'taux' else rep.fixe_enregistrement,
				'base_enregistrement': float(rep.dossier_id.montant_transaction) if rep.type_enregistrement == 'taux' else 0 ,
				'taux_enregistrement': float(rep.taux_enregistrement) if rep.type_enregistrement == 'taux' else 0 ,
				}, context={'enregistrement_ok' : True})


		if rep.conservation_ok :
			pr_id = self.pool.get('conservation.fonciere').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'conservation.fonciere'),
				'state': 'draft',
				'libelle': rep.libelle_id.name,
				'repertoire_id': rep.id,
				'executeur_certificat_id':rep.executeur_certificat_id.id,
				'date_cf': time.strftime('%Y-%m-%d %H:%M:%S'),
				'delai_cf': rep.delai_conservation,
		                'libelle': rep.libelle_id.name,
				'delai_cf': rep.delai_conservation,
		                'montant_systeme': rep.taux_cons* rep.dossier_id.montant_transaction if rep.type_conservation == 'taux' else rep.fixe_cons,
				'base_conservation': float(rep.dossier_id.montant_transaction) if rep.type_conservation == 'taux' else 0 ,
				'taux_conservation': float(rep.taux_cons / 100 )  if rep.type_conservation == 'taux' else 0 ,
		               
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,
				'tf_objet':rep.dossier_id.tf_objet,
				'date_creation_repertoire':rep.date_creation_repertoire,
				'lieu_con_id':rep.dossier_id.lieu_objet,
				} , context={'conservation_ok' : True})
		if not rep.conservation_ok :
			pr_id = self.pool.get('conservation.fonciere').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'conservation.fonciere'),
				'state': 'pas_conservation',
				'repertoire_id': rep.id,
				'date_cf': rep.date_validation,
				'delai_cf': 0,
		                'libelle': rep.libelle_id.name,
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,
				'tf_objet':rep.dossier_id.tf_objet,
				} , context={'conservation_ok' : True})
		if rep.quitus_ok :

			pr_id = self.pool.get('notariat.quitus').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'notariat.quitus'),
				'state': 'draft',
				'repertoire_id': rep.id,
				'date_creation_repertoire': rep.date_creation_repertoire,
				'date_demande_quitus':time.strftime('%Y-%m-%d %H:%M:%S'),
				'demandeur_id':uid,
				'partie1':rep.dossier_id.partie1,
				'partie2':rep.dossier_id.partie2,
				'partie3':rep.dossier_id.partie3,
				'tf_objet':rep.dossier_id.tf_objet,
				} , context={'quitus_ok' : True})

		if rep.impot_tpi_ok :
			pr_id = self.pool.get('impot.tpi').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'impot.tpi'),
				'state': 'draft',
				'repertoire_id': rep.id,
				'date_creation_repertoire': rep.date_creation_repertoire,
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,
		                'type_tpi': rep.type_tpi,
		                'delai_tpi': rep.delai_tpi,
				'tf_objet':rep.dossier_id.tf_objet,
				}, context={'impot_tpi_ok' : True})

		if rep.impot_te_ok :
			pr_id = self.pool.get('impot.te').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'impot.te'),
				'state': 'draft',
				'repertoire_id': rep.id,
				'date_creation_repertoire': rep.date_creation_repertoire,
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,
		                'type_te': rep.type_tpi,
		                'delai_te': rep.delai_tpi,
				'tf_objet':rep.dossier_id.tf_objet,
				}, context={'impot_te_ok' : True})


		if rep.impot_tnb_ok :
			pr_id = self.pool.get('impot.tnb').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'impot.tnb'),
				'state': 'draft',
				'repertoire_id': rep.id,
				'date_creation_repertoire': rep.date_creation_repertoire,
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,
		                'type_tnb': rep.type_tnb,
		                'delai_tnb': rep.delai_tnb,
				'tf_objet':rep.dossier_id.tf_objet,
				}, context={'impot_tnb_ok' : True})
		if rep.banque_ok :
			pr_id = self.pool.get('notariat.banque').create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, 'notariat.banque'),
				'state': 'draft',
				'repertoire_id': rep.id,
				'date_creation_repertoire': rep.date_creation_repertoire,
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,
				'tf_objet':rep.dossier_id.tf_objet,
				}, context={'banque_ok' : True})

		return self.write(cr, uid, ids, {'state': 'repertorie','name':self.pool.get('ir.sequence').get(cr, uid, 'notariat.repertoire'),}, context=None)


    def rep_valide(self, cr, uid, ids, *args):
		rep = self.browse(cr, uid, ids)[0]
		if rep.certification_ok :
			for obj in rep.dossier_id.biens_ids :
		                 pr_id = self.pool.get('notariat.propriete').create(cr, uid, {
		                'name':self.pool.get('ir.sequence').get(cr, uid, 'notariat.propriete'),
		                'state': 'draft',
		                'repertoire_id': rep.id,
		                'libelle': rep.libelle_id.name,
		                'date_cp': time.strftime('%Y-%m-%d %H:%M:%S'),
				'date_creation_repertoire': rep.date_creation_repertoire,
		                'bien_id': obj.id,
		                'lieu_con_id': obj.lieu_conservation.id,
		                'executeur_certificat_id': rep.executeur_certificat_id.id,
		                'partie1': rep.dossier_id.partie1,
		                'partie2': rep.dossier_id.partie2,
		                'partie3': rep.dossier_id.partie3,

		                }, context={'certification_ok' : True})

		return self.write(cr, uid, ids, {'state': 'valide', 'date_validation': time.strftime('%Y-%m-%d %H:%M:%S'),'user_id':uid,}, context=None)




    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft']:
            	unlink_ids.append(s['id'])
            else:
            	raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des répertoires en mode Brouillon! Vous pouvez uniquement les annluer!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)



notariat_repertoire()

####### Quitus ######################################################

class notariat_quitus(osv.osv):
    _name = 'notariat.quitus'
    _inherit = ['mail.thread']
    _columns = {
        'name' : fields.char(u'Numéro quitus',size=50),
        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'reference_quitus': fields.char(u'Référence quitus', size=64),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'demandeur_id':fields.many2one('res.users',u'Demandé par'),
        'executeur_id':fields.many2one('res.users',u'Executé par'),
        'date_demande_quitus' : fields.date(u'Date demande quitus'),
        'date_creation_repertoire' : fields.date(u'Date Création Rép'),
        'date_quitus' : fields.date(u'Date quitus'),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], 'Etat Quitus'),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'tf_objet': fields.char(u'LES TF', size=200),
        'date_signature_quitus' : fields.datetime(u'Date/Heure Signature Quitus'),



    }


    _order = "dossier_id desc"

    _defaults = {


        'date_demande_quitus' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
	'name': lambda self, cr, uid, context: '/',
	'state': lambda object,cr,uid,context: 'draft',


    }




    def create(self, cr, uid, vals, context={}):
#        context={'quitus_ok' : True}
	print """"quitus_ok"""
        if not context.get('quitus_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer un quitus, vous devez passer par le dossier puis initialiser contrat.')
        return  super(notariat_quitus,self).create(cr, uid, vals, context=context)




    def quitus_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel','executeur_id':uid}, context=None)


    def quitus_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide','executeur_id':uid,'date_quitus':time.strftime('%Y-%m-%d %H:%M:%S')}, context=None)



    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
            	unlink_ids.append(s['id'])
            else:
            	raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des quitus validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)



notariat_quitus()


####### Enregistrement ###########################################


class notariat_enregistrement(osv.osv):
    _name = 'notariat.enregistrement'
    _inherit = ['mail.thread']


    def _get_montant_total_systeme(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.montant_systeme) + float(line.montant_timbre) + float(line.montant_taxe)
        return res 


    _columns = {

        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'name' : fields.char(u'Numéro enregistrement',size=50),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'dv_enregistrement':fields.related('depot_id','dv_enregistrement', type="char", relation="depot.enregistrement", string=u"DV"),
        'or_enregistrement':fields.related('depot_id','or_enregistrement', type="char", relation="depot.enregistrement", string=u"OR"),
        're_enregistrement':fields.related('depot_id','re_enregistrement', type="char", relation="depot.enregistrement", string=u"RE"),
        'e17b_enregistrement':fields.related('depot_id','e17b_enregistrement', type="char", relation="depot.enregistrement", string=u"E17B"),

        'date_enregistrement' : fields.date(u'Date enregistrement'),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'date_demande_enregistrement' : fields.date(u'Date Demande Enreg'),
        'date_depot':fields.related('depot_id','date_depot', type="date", relation="depot.enregistrement", string=u"Date dépôt"),
        'numero_depot':fields.related('depot_id','name_depot', type="char", relation="depot.enregistrement", string=u"Numéro dépôt enregistrement"),
        'observation' : fields.text(u'Observation'),
        'montant_timbre':fields.float(u'Montant timbre'),
        'montant_taxe':fields.float(u'Montant taxe'),
        'montant_paye':fields.float(u'Montant payé'),
        'montant_systeme':fields.float(u'Montant enregistrement système'),
        'montant_total': fields.function(_get_montant_total_systeme, method=True, type='float', string='Montant Total Système' ,store=True),
        'client_id' : fields.many2one('res.partner',u'Client'),

        'libelle': fields.char(u'Libellé', size=64),
        'base_enregistrement':fields.float(u'Base'),
        'taux_enregistrement':fields.float(u'Taux'),

        'depot_id':fields.many2one('depot.enregistrement',u'Dépôt'),
        'ref_paiement_enregistrement' : fields.char(u'Réf paiement enregistrement',size=50),
        'date_signature_enregistrement' : fields.datetime(u'Date/Heure Signature Enregistrement'),

        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], 'Etat enregistrement'),



    }

    _defaults = {
		'name': lambda self, cr, uid, context: '/',
        	'state': lambda *a: 'draft',



		}

    _order = "dossier_id desc"



    def create(self, cr, uid, vals, context={}):
        #context={'enregistrement_ok' : True}
        print """"create enregistrement_ok"""
        if not context.get('enregistrement_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer un enregistrement, vous devez passer par le dossier puis initialiser contrat.')
        return  super(notariat_enregistrement,self).create(cr, uid, vals, context=context)

            



    def eng_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def eng_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)



    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des enregistrements validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)



notariat_enregistrement()


####### DEPOT Enregistrement : UN DEPOT ENREGISTREMENT A PLUSIEURS LIGNES ENREGISTREMENT  ###########################################


class depot_enregistrement(osv.osv):
    _name = 'depot.enregistrement'



    def _get_montant_depot(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            montant_depot = 0
            for enreg in line.enregistrements_id:
                montant_depot += float(enreg.montant_total)
            res[line.id] = montant_depot
            return res 

    _columns = {


        'date_depot' : fields.date(u'Date dépôt'),
        'name' : fields.char(u'Numéro',size=50),
        'name_depot' : fields.char(u'Numéro dépôt',size=50),
        'observation' : fields.text(u'Observation'),
        'enregistrements_id': fields.one2many('notariat.enregistrement', 'depot_id', u'Enregistrements'),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], 'Etat DEPOT enregistrement'),
        'dv_enregistrement' : fields.char(u'DV',size=50),
        'or_enregistrement' : fields.char(u'OR',size=50),
        're_enregistrement' : fields.char(u'RE',size=50),
        'e17b_enregistrement' : fields.char(u'E17B',size=50),
        'montant_depot': fields.function(_get_montant_depot, method=True, type='float', string='Montant dépôt' ,store=True),

    }

    _defaults = {
		'name': lambda self, cr, uid, context: '/',
        	'state': lambda *a: 'draft',
        	'date_depot' :lambda *a: time.strftime('%Y-%m-%d'),


		}

    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'depot.enregistrement')
        return super(depot_enregistrement,self).create(cr, user, vals, context)




    def depot_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def depot_valide(self, cr, uid, ids, context=None):
        for depot in self.browse(cr,uid,ids):
            self.pool.get('notariat.enregistrement').conservation_valide(cr,uid,[cf.id for cf in depot.enregistrements_id])
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)



    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des DEPOTS ENREGISTREMENTS validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)


depot_enregistrement()


####### Recette CONSERVARTION FONCIERE : UNE RECETTE CONSERVATIONS A PLUSIEURS LIGNES CONSERVATION ###########################################


class recette_conservation(osv.osv):
    _name = 'recette.conservation'


    def _get_montant_recette(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            montant_recette = 0
            for cons in line.conservations_id:
                montant_recette += float(cons.montant_paye)
            res[line.id] = montant_recette
            return res 

    _columns = {


        'date_recette' : fields.date(u'Date recette'),
        'name' : fields.char(u'Numéro recette',size=50),
        'numero_serie' : fields.char(u'Numéro série',size=50),
        'observation' : fields.text(u'Observations'),
        'conservations_id': fields.one2many('conservation.fonciere', 'recette_id', u'Conservations'),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], 'Etat Recette'),
        'montant_recette': fields.function(_get_montant_recette, method=True, type='float', string='Montant Recette', store=True),
        'client_id' : fields.many2one('res.partner',u'Client'),

    }

    _defaults = {
		'name': lambda self, cr, uid, context: '/',
        	'state': lambda *a: 'draft',


		}



    def recette_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def recette_valide(self, cr, uid, ids, context=None):	
        for recette in self.browse(cr,uid,ids):
            self.pool.get('conservation.fonciere').conservation_valide(cr,uid,[cf.id for cf in recette.conservations_id])
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)


    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des RECETTES DE C.F validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)


recette_conservation()





####### Conservation Fonciere ###########################################


class conservation_fonciere(osv.osv):
    _name = 'conservation.fonciere'
    _inherit = ['mail.thread']



    def _get_last_retour(self, cr, uid, ids, name, args, context):
        res = {}
        obj_cons = self.pool.get('retour.conservation')
        for cons in self.browse(cr, uid, ids, context=context):
            cons_ids = obj_cons.search(cr, uid, [('cf_id','=',cons.id),], order='retourne_le', context=context)
            if cons_ids:
                res[cons.id] = cons_ids[-1:][0]
                res[cons.id] = obj_cons.browse(cr, uid, cons_ids[-1:][0], context=context).retourne_le
            else:
                res[cons.id] = False
        return res


    def _get_premier_depot(self, cr, uid, ids, name, args, context):
        res = {}
        obj_cons = self.pool.get('retour.conservation')
        for cons in self.browse(cr, uid, ids, context=context):
            cons_ids = obj_cons.search(cr, uid, [('cf_id','=',cons.id),], order='depose_le', context=context)
            if cons_ids:
                res[cons.id] = cons_ids[0]
                res[cons.id] = obj_cons.browse(cr, uid, cons_ids[0], context=context).depose_le
            else:
                res[cons.id] = False
        return res



    def _get_montant_total_systeme(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.montant_systeme) + float(line.montant_timbre) + float(line.montant_taxe)
        return res 



    def conservation_fonciere_echus(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for cons in self.browse(cr, uid, ids, context=context):
            if cons.compteur_store :
                res[cons.id] = cons.compteur_store
            else :
                compteur_mtn = 0
                date_creation_repertoire= cons.date_creation_repertoire
                date_mtn= time.strftime('%Y-%m-%d')
                date_creation_repertoire = date_creation_repertoire.split('-')
                date_mtn= date_mtn.split('-')
                jours1 = 0
                jours2 = 0
                jours1 = ((int(date_mtn[0]) * 365) + (int(date_mtn[1]) * 30) + int((date_mtn[2])))
                print jours1
                jours2 = ((int(date_creation_repertoire[0]) * 365) + (int(date_creation_repertoire[1]) * 30) + int((date_creation_repertoire[2])))
                print jours2
                compteur = (jours1 - jours2)
                print compteur
                res[cons.id] = compteur
        return res




    def write(self, cr, uid, ids, vals, context=None):
        for id in ids:
            if vals.get('state', '') in ['Valide','cancel']:
                vals['compteur_store'] = self.read(cr, uid, id, ['compteur'])['compteur']
        res = super(conservation_fonciere, self).write(cr, uid, ids, vals, context=context)
        return res


 
    _columns = {
        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'name' : fields.char(u'N° C.F', size=200),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'libelle': fields.char(u'Libellé', size=64),
        'numero_recette':fields.related('recette_id','name', type="char", relation="recette.conservation", string=u"Numéro Recette"),
        'date_cf' : fields.date(u'Date CF',help=u'Date de répertoire'),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé'),('pas_conservation', u'Pas de CF')], 'Etat CF'),
        'retour_id': fields.one2many('retour.conservation', 'cf_id', 'Retours'),

        'last_retour': fields.function(_get_last_retour, method=True, type='date', string=u'Dernier retour'),
        'premier_depot': fields.function(_get_premier_depot, method=True, type='date', string=u'Premier dépôt à la C.F'),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'date_creation_repertoire' : fields.date(u'Date Création Rép'),
        'tf_objet': fields.char(u'LES TF', size=200),
        'lieu_con_id':fields.char(u'LIEU CF', size=200),
        'compteur': fields.function(conservation_fonciere_echus, type="float", string='Délai en j'),
	    'compteur_store': fields.float("not used"),
        'delai_cf': fields.float(u'Délai permis', digits=(16,2)),
        'date_enregistrement' : fields.date(u'Enreg le'),

        'montant_timbre':fields.float(u'Montant timbre'),
        'montant_taxe':fields.float(u'Montant taxe'),
        'montant_paye':fields.float(u'Montant payé'),
        'montant_systeme':fields.float(u'Montant C.F système'),
        'montant_total': fields.function(_get_montant_total_systeme, method=True, type='float', string='Montant Total Système' ,store=True),
        'base_conservation':fields.float(u'Base'),
        'taux_conservation':fields.float(u'Taux'),
        'recette_id':fields.many2one('recette.conservation',u'Recette'),
        'client_id' : fields.many2one('res.partner',u'Client'),
        'date_signature_cf' : fields.datetime(u'Date/Heure Signature CF'),


    }



    _defaults = {
		'name': lambda self, cr, uid, context: '/',
        'state': lambda *a: 'draft',
		}


    _order = "dossier_id desc"


    def create(self, cr, uid, vals, context={}):
        print """"conservation_ok"""
        if not context.get('conservation_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer une conservation foncière, vous devez passez par le dossier puis initialiser contrat.')
        return  super(conservation_fonciere,self).create(cr, uid, vals, context=context)


    def conservation_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def conservation_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)


    def conservation_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)


    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des C.F validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
conservation_fonciere()


###### SUIVI DES RETOURS DE LA CONSERVATION FONCIERE ###########################################


class retour_conservation(osv.osv):
    _name = 'retour.conservation'
    _columns = {

        'depose_le' : fields.date(u'Déposé le'),
        'retourne_le' : fields.date(u'Retourné le'),
        'observation' : fields.text(u'Observation'),
        'cf_id':fields.many2one('conservation.fonciere',u'CF'),
        'dossier_id':fields.related('cf_id', 'dossier_id','repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),


    }



retour_conservation()


############# Impot TPI ########################################


class impot_tpi(osv.osv):
    _name = 'impot.tpi'
    _inherit = ['mail.thread']


    def create(self, cr, uid, vals, context={}):
        #context={'impot_tpi_ok' : True}
        print """"create impot TPI"""
        if not context.get('impot_tpi_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer un Impôt TPI, vous devez passer par le dossier puis initialiser contrat.')
        return  super(impot_tpi,self).create(cr, uid, vals, context=context)

            




    def impot_tpi_echus(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for tpi in self.browse(cr, uid, ids, context=context):
            if tpi.compteur_store :
                res[tpi.id] = tpi.compteur_store
            else :
                compteur_mtn = 0
                date_creation_repertoire= tpi.date_creation_repertoire
                date_mtn= time.strftime('%Y-%m-%d')
                date_creation_repertoire = date_creation_repertoire.split('-')
                date_mtn= date_mtn.split('-')
                jours1 = 0
                jours2 = 0
                jours1 = ((int(date_mtn[0]) * 365) + (int(date_mtn[1]) * 30) + int((date_mtn[2])))
                print jours1
                jours2 = ((int(date_creation_repertoire[0]) * 365) + (int(date_creation_repertoire[1]) * 30) + int((date_creation_repertoire[2])))
                print jours2
                compteur = (jours1 - jours2)
                print compteur
                res[tpi.id] = compteur
        return res




    def write(self, cr, uid, ids, vals, context=None):
        #MOD
        for id in ids:
            if vals.get('state', '') in ['Valide','cancel']:
                vals['compteur_store'] = self.read(cr, uid, id, ['delai_realisation'])['delai_realisation']
            res = super(impot_tpi, self).write(cr, uid, id, vals, context=context)
        return res


    def _get_benifice_suppose_systeme(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.prix_vente_tpi) - ( ( float(line.prix_achat_tpi) * 0.15 + float(line.prix_achat_tpi) ) * float(line.coeff_tpi))
        return res 


    def _get_impot_benifice_suppose_systeme(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):

            res[line.id] =( float(line.prix_vente_tpi) - ( ( float(line.prix_achat_tpi) * 0.15 + float(line.prix_achat_tpi) ) * float(line.coeff_tpi)) ) * float(line.pourcentage_impot / 100)

        return res 


    def _get_cotisation_minimale_systeme(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):

            res[line.id] =float(line.coeff_cotisation_minimale / 100) * float(line.prix_vente_tpi)
        return res 



    def _get_impot_payer_systeme(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if  line.impot_benifice_suppose < line.coeff_cotisation_minimale :
                res[line.id] = line.coeff_cotisation_minimale 
            else:
                res[line.id] = line.impot_benifice_suppose
        return res 





    _columns = {
        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'name' : fields.char(u'Numéro',size=50),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'date_creation_repertoire' : fields.date(u'Date Création Rép'),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'type_tpi' : fields.selection([('client',u'A la charge du client'),('cabinet',u'A la charge du cabinet')],u'A la charge'),
        'date_decharge_client' : fields.date(u'Date décharge client'),
        'montant_paye':fields.float(u'Montant payé'),
        'date_paiement' : fields.date(u'Date paiement'),
        'delai_realisation': fields.function(impot_tpi_echus, type="float", string='Délai de réalisation'),
	    'compteur_store': fields.float("not used"),
        'delai_tpi':fields.float(u'Délai permis pour la tpi'),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], u'Etat Impôt TPI'),
        'reference_paiement': fields.char(u'Référence paiement', size=64),
        'tf_objet': fields.char(u'N° Titre foncier', size=64),
        'client_id' : fields.many2one('res.partner',u'Client'),
        'date_signature_tpi' : fields.datetime(u'Date/Heure Signature TPI'),
        'prix_vente_tpi':fields.float(u'Prix de vente', digits=(16,4)),
        'prix_achat_tpi':fields.float(u'Prix d\'achat', digits=(16,4)),
        'annee_achat_tpi' : fields.integer(u'Année d\'achat',size=4),
        'coeff_tpi' : fields.float(u'Coefficient', digits=(16,4)),


        'benifice_suppose': fields.function(_get_benifice_suppose_systeme, method=True, type='float', string=u'Bénifice supposé', digits=(16,2)),
        'pourcentage_impot' : fields.float(u'% Impôt', digits=(16,4)),
        'impot_benifice_suppose': fields.function(_get_impot_benifice_suppose_systeme, method=True, type='float', string=u'Impôt sur Bénifice supposé', digits=(16,2)),

        'coeff_cotisation_minimale' : fields.float(u'Coefficient Cotisation minimale', digits=(16,4)),
        'cotisation_minimale': fields.function(_get_cotisation_minimale_systeme, method=True, type='float', string=u'Cotisation Minimale', digits=(16,2)),

        'impot_payer': fields.function(_get_impot_payer_systeme, method=True, type='float', string=u'Impôt A Payer', digits=(16,2)),



    }



    _defaults = {
		'name': lambda self, cr, uid, context: '/',
		'state': lambda object,cr,uid,context: 'draft',
		'coeff_cotisation_minimale': 3,
		'pourcentage_impot': 20,



		}

    _order = "dossier_id desc"






    def tpi_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def tpi_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)


    def tpi_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)




    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des IMPOTS TPI validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)



impot_tpi()

####### Certificat PROPRIETE ######################################################

class notariat_propriete(osv.osv):
    _name = 'notariat.propriete'
    _inherit = ['mail.thread']





    def certificat_propriete_echus(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for cp in self.browse(cr, uid, ids, context=context):
            if cp.compteur_store :
                res[cp.id] = cp.compteur_store
            else :
                compteur_mtn = 0
                date_creation_repertoire= cp.date_cp
                date_mtn= time.strftime('%Y-%m-%d')
                date_creation_repertoire = date_creation_repertoire.split('-')
                date_mtn= date_mtn.split('-')
                jours1 = 0
                jours2 = 0
                jours1 = ((int(date_mtn[0]) * 365) + (int(date_mtn[1]) * 30) + int((date_mtn[2])))
                print jours1
                jours2 = ((int(date_creation_repertoire[0]) * 365) + (int(date_creation_repertoire[1]) * 30) + int((date_creation_repertoire[2])))
                print jours2
                compteur = (jours1 - jours2)
                print compteur
                res[cp.id] = compteur
        return res




    def write(self, cr, uid, ids, vals, context=None):
        #MOD
        for id in ids:
            if vals.get('state', '') in ['Valide','cancel']:
                vals['compteur_store'] = self.read(cr, uid, id, ['compteur'])['compteur']
            res = super(notariat_propriete, self).write(cr, uid, id, vals, context=context)
        return res





    _columns = {
        'name' : fields.char(u'Numéro CP',size=50),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'libelle': fields.char(u'Libellé', size=64),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'date_creation_repertoire' : fields.date(u'Date Création Rép'),
        'executeur_certificat_id':fields.many2one('res.users',u'Executé par'),
        'date_cp' : fields.date(u'Demande effectué le',help=u'Date demande CP'),
        'date_reception_propriete' : fields.date(u'Document reçu le'),
        'compteur': fields.function(certificat_propriete_echus, type="float", string='Délai en j'),
	    'compteur_store': fields.float("not used"),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], 'Etat Certificat propriété'),
        'bien_id':fields.many2one('notariat.bien',u'N° TF'),
        'lieu_con_id':fields.many2one('lieu.conservation',u'Lieu conservation'),
        'date_signature_cp' : fields.datetime(u'Date/Heure Signature CP'),

    }
    _defaults = {
		'name': lambda self, cr, uid, context: '/',
        	'state': lambda *a: 'draft',



		}

    _order = "dossier_id desc"


    def create(self, cr, user, vals, context=None):
        #mod
        if context and not context.get('certification_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer une Certificat. de propriété vous devez passer par le dossier puis initialiser contrat.')
        #mod
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'notariat.propriete')
        return super(notariat_propriete,self).create(cr, user, vals, context)


    
    #def create(self, cr, uid, vals, context={}):
        #print """"certification_ok"""
        #if not context.get('certification_ok',False):
            #raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer une Certificat. de propriété vous devez passer par le dossier puis initialiser contrat.')
        #return  super(notariat_propriete,self).create(cr, uid, vals, context=context)

            



    def propriete_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def propriete_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide','executeur_certificat_id':uid,'date_reception_propriete':time.strftime('%Y-%m-%d %H:%M:%S')}, context=None)


    def propriete_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)





    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des C.P validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)







notariat_propriete()



####### Suivi banque ######################################################

class notariat_banque(osv.osv):
    _name = 'notariat.banque'
    _inherit = ['mail.thread']
    _columns = {
        'name' : fields.char(u'Numéro suivi',size=50),
        'date_remis_doc' : fields.date(u'Doc Remis au client le'),
        'date_recus_doc' : fields.date(u'Doc Reçus le'),
        'date_redaction_contrat' : fields.date(u'Contrat rédigé le '),
        'date_envoi_contrat' : fields.date(u'Contrat envoyé le '),
        'date_signature_contrat' : fields.date(u'Contrat signé reçu le '),
        'date_encaissement_recu' : fields.date(u'Encaissement reçu le'),
        'date_debut_delai' : fields.date(u'Début délai engagement le'),
        'date_doc_definitif' : fields.date(u'Doc. Définitifs envoyés le'),
        'reference_doc_recu' : fields.char(u'Références',size=50),
        'reference_redaction_contrat' : fields.char(u'Références',size=50),
        'reference_envoi_contrat' : fields.char(u'Références',size=50),
        'reference_signature_contrat' : fields.char(u'Références',size=50),
        'reference_encaissement_recu' : fields.char(u'Références',size=50),
        'delai': fields.float(u'Délai en j', digits=(16,2)),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'tf_objet': fields.char(u'N° Titre foncier', size=64),
        'date_creation_repertoire' : fields.date(u'Date Création Rép'),
        'banque_id':fields.many2one('res.bank',u'Banque'),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], 'Etat Suivi Banque'),
        'montant_demande': fields.float(u'Montant demandé', digits=(16,2)),
        'client_id' : fields.many2one('res.partner',u'Client'),




    }

    _order = "dossier_id desc"


    _defaults = {
		'name': lambda self, cr, uid, context: '/',
        	'state': lambda *a: 'draft',
        	'delai': 30,



		}



    def create(self, cr, user, vals, context=None):
        #mod
        if context and not context.get('banque_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer un suivi de la banque, vous devez passer par le dossier puis initialiser contrat.')
        #mod
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'notariat.banque')
        return super(notariat_banque,self).create(cr, user, vals, context)


    #def create(self, cr, uid, vals, context={}):
#        context={'banque_ok' : True}
        #if not context.get('banque_ok',False):
            #raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer un suivi de la banque, vous devez passer par le dossier puis initialiser contrat.')
        #return  super(notariat_banque,self).create(cr, uid, vals, context=context)

            



    def banque_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def banque_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)


    def banque_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)



    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des lignes de suivi de la BANQUE validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)





notariat_banque()



############# Impot TE ########################################



class impot_te(osv.osv):
    _name = 'impot.te'
    _inherit = ['mail.thread']



    def impot_te_echus(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for te in self.browse(cr, uid, ids, context=context):
            if te.compteur_store :
                res[te.id] = te.compteur_store
            else :
                compteur_mtn = 0
                date_creation_repertoire= te.date_creation_repertoire
                date_mtn= time.strftime('%Y-%m-%d')
                date_creation_repertoire = date_creation_repertoire.split('-')
                date_mtn= date_mtn.split('-')
                jours1 = 0
                jours2 = 0
                jours1 = ((int(date_mtn[0]) * 365) + (int(date_mtn[1]) * 30) + int((date_mtn[2])))
                print jours1
                jours2 = ((int(date_creation_repertoire[0]) * 365) + (int(date_creation_repertoire[1]) * 30) + int((date_creation_repertoire[2])))
                print jours2
                compteur = (jours1 - jours2)
                print compteur
                res[te.id] = compteur
        return res



    def write(self, cr, uid, ids, vals, context=None):
        #MOD
        for id in ids:
            if vals.get('state', '') == 'Valide':
                vals['compteur_store'] = self.read(cr, uid, id, ['delai_realisation'])['delai_realisation']
            res = super(impot_te, self).write(cr, uid, id, vals, context=context)
        return res


    _columns = {
        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'name' : fields.char(u'Numéro',size=50),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'date_creation_repertoire' : fields.date(u'Date Création Rép'),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'type_te' : fields.selection([('client',u'A la charge du client'),('cabinet',u'A la charge du cabinet')],u'A la charge'),
        'date_decharge_client' : fields.date(u'Date décharge client'),
        'montant_paye':fields.float(u'Montant payé'),
        'date_paiement' : fields.date(u'Date paiement'),
        'delai_realisation': fields.function(impot_te_echus, type="float", string='Délai de réalisation'),
	    'compteur_store': fields.float("not used"),
        'delai_te':fields.float(u'Délai permis pour la te'),
        'state':fields.selection([('draft', u'Brouillon'),('Valide', u'Validé'),('cancel', u'Annulé')], u'Etat Impôt TE'),
        'reference_paiement': fields.char(u'Référence paiement', size=64),
        'tf_objet': fields.char(u'N° Titre foncier', size=64),
        'client_id' : fields.many2one('res.partner',u'Client'),
        'date_signature_te' : fields.datetime(u'Date/Heure Signature TE'),


    }



    _defaults = {
		'name': lambda self, cr, uid, context: '/',
		'state': lambda object,cr,uid,context: 'draft',

		}

    _order = "dossier_id desc"


    def create(self, cr, uid, vals, context={}):
        #context={'impot_te_ok' : True}
        print """"create impot TE"""
        if not context.get('impot_te_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer un Impôt TE, vous devez passer par le dossier puis initialiser contrat.')
        return  super(impot_te,self).create(cr, uid, vals, context=context)

            




    def te_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def te_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)


    def te_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)






    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des IMPOTS TE validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)






impot_te()

############# Impot TNB ########################################



class impot_tnb(osv.osv):
    _name = 'impot.tnb'
    _inherit = ['mail.thread']

    def impot_tnb_echus(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for tnb in self.browse(cr, uid, ids, context=context):
            if tnb.compteur_store :
                res[tnb.id] = tnb.compteur_store
            else :
                compteur_mtn = 0
                date_creation_repertoire= tnb.date_creation_repertoire
                date_mtn= time.strftime('%Y-%m-%d')
                date_creation_repertoire = date_creation_repertoire.split('-')
                date_mtn= date_mtn.split('-')
                jours1 = 0
                jours2 = 0
                jours1 = ((int(date_mtn[0]) * 365) + (int(date_mtn[1]) * 30) + int((date_mtn[2])))
                print jours1
                jours2 = ((int(date_creation_repertoire[0]) * 365) + (int(date_creation_repertoire[1]) * 30) + int((date_creation_repertoire[2])))
                print jours2
                compteur = (jours1 - jours2)
                print compteur
                res[tnb.id] = compteur
        return res



    def write(self, cr, uid, ids, vals, context=None):
        for id in ids:
            if vals.get('state', '') in ['Valide','cancel']:
                vals['compteur_store'] = self.read(cr, uid, id, ['delai_realisation'])['delai_realisation']
            res = super(impot_tnb, self).write(cr, uid, id, vals, context=context)
        return res



    _columns = {
        'dossier_id':fields.related('repertoire_id','dossier_id', type="many2one", relation="notariat.dossier", string=u"N° Dossier", store=True),
        'name' : fields.char(u'Numéro',size=50),
        'repertoire_id':fields.many2one('notariat.repertoire',u'Répertoire'),
        'date_creation_repertoire' : fields.date(u'Date Création Rép'),
        'partie1': fields.char(u'Partie 1', size=200),
        'partie2': fields.char(u'Partie 2', size=200),
        'partie3': fields.char(u'Partie 3', size=200),
        'type_tnb' : fields.selection([('client',u'A la charge du client'),('cabinet',u'A la charge du cabinet')],u'A la charge'),
        'date_decharge_client' : fields.date(u'Date décharge client'),
        'montant_paye':fields.float(u'Montant payé'),
        'date_paiement' : fields.date(u'Date paiement'),
        'delai_realisation': fields.function(impot_tnb_echus, type="float", string='Délai de réalisation'),
        'delai_tnb':fields.float(u'Délai permis pour la tnb'),
	    'compteur_store': fields.float("not used"),
        'state':fields.selection([('draft', u'Ouvert'),('Valide', u'Validé'),('cancel', u'Annulé')], u'Etat Impôt TNB'),
        'reference_paiement': fields.char(u'Référence paiement', size=64),
        'tf_objet': fields.char(u'N° Titre foncier', size=64),
        'client_id' : fields.many2one('res.partner',u'Client'),
        'date_signature_tnb' : fields.datetime(u'Date/Heure Signature TNB'),


    }



    _defaults = {
		'name': lambda self, cr, uid, context: '/',
		'state': lambda object,cr,uid,context: 'draft',
		}


    _order = "dossier_id desc"

    def create(self, cr, uid, vals, context={}):
        #context={'impot_tnb_ok' : True}
        print """"create impot TNB"""
        if not context.get('impot_tnb_ok',False):
            raise osv.except_osv(u'Procédure incorrecte !',u'Pour créer un Impôt TNB, vous devez passer par le dossier puis initialiser contrat.')
        return  super(impot_tnb,self).create(cr, uid, vals, context=context)

            




    def tnb_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=None)


    def tnb_valide(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Valide'}, context=None)


    def tnb_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=None)


    def unlink(self, cr, uid, ids, context=None):
        dossiers = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in dossiers:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Action non valide  !'), _('Vous ne pouvez pas supprimer des IMPOTS TNB validés!'))
            return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)



impot_tnb()


#### DESGNATION BIEN ###########################"

class designation_bien(osv.osv):
    _name = 'designation.bien'

    _columns = {

        'code' : fields.char(u'Code Désignation Bien',size=50, required=True),
        'name' : fields.char(u'Nom Désignation Bien',size=50, required=True),

    }

designation_bien()


#### PROPRIETAIRE BIEN ###########################"

class proprietaire_bien(osv.osv):
    _name = 'proprietaire.bien'

    _columns = {

        'client_id' : fields.many2one('res.partner',u'Client'),
        'quote_part' : fields.char(u'Quote Part',size=50),
	'bien_id': fields.many2one('notariat.bien',u'Bien'),

    }


proprietaire_bien()		             

#### CONSULTATION BIEN ###########################"

class consultation_bien(osv.osv):
    _name = 'consultation.bien'

    _columns = {

        'user_consultation_id' : fields.many2one('res.users',u'Consulté(e) par'),
        'date_consultation' : fields.datetime(u'Date/Heure Consultation'),
	'bien_id': fields.many2one('notariat.bien',u'Bien'),
	'file_id': fields.many2one('ir.attachment',u'Pièce jointe'),


    }

    _order = "date_consultation"


    _defaults = {


        'date_consultation' :lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_consultation_id': lambda object,cr,uid,context: uid,


    }




consultation_bien()

#### TYPE PAIEMENT PRIX ###########################"

class type_montant(osv.osv):
    _name = 'type.montant'

    _columns = {

        'name' : fields.char(u'Type paiement prix',size=50, required=True),

    }

type_montant()







