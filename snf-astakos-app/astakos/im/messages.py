# Copyright 2011-2012 GRNET S.A. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of GRNET S.A.

ACCOUNT_AUTHENTICATION_FAILED           =   'Cannot authenticate account.'
ACCOUNT_ALREADY_ACTIVE                  =   'Account is already active.'
ACCOUNT_PENDING_ACTIVATION              =   'Your request is pending activation.'
ACCOUNT_RESEND_ACTIVATION               =   'You have not followed the activation link. <a href="%(send_activation_url)s">Resend activation email?</a>'
INACTIVE_ACCOUNT_CHANGE_EMAIL           =   ''.join([ACCOUNT_RESEND_ACTIVATION, ' or <a href="%(signup_url)s">Provide new email?</a>'])

ACCOUNT_UNKNOWN                         =   'There is no such account.'
TOKEN_UNKNOWN                           =   'There is no user matching this token.'

PROFILE_UPDATED                         =   'Profile has been updated successfully.'
FEEDBACK_SENT                           =   'Feedback successfully sent.'
EMAIL_CHANGED                           =   'Account email has been changed successfully.'
EMAIL_CHANGE_REGISTERED                 =   'Change email request has been registered succefully. \
                                               You are going to receive a verification email in the new address.'

OBJECT_CREATED                          =   'The %(verbose_name)s was created successfully.'
MEMBER_JOINED_GROUP                     =   '%(realname)s has been successfully joined the group.'
MEMBER_REMOVED                          =   '%(realname)s has been successfully removed from the group.'
BILLING_ERROR                           =   'Service response status: %(status)d' 
LOGOUT_SUCCESS                          =   'You have successfully logged out.'

GENERIC_ERROR                           =   'Something wrong has happened. \
                                               Please contact the administrators for more details.'

MAX_INVITATION_NUMBER_REACHED   =           'There are no invitations left.'
GROUP_MAX_PARTICIPANT_NUMBER_REACHED    =   'Group maximum participant number has been reached.'
NO_APPROVAL_TERMS                       =   'There are no approval terms.'
PENDING_EMAIL_CHANGE_REQUEST            =   'There is already a pending change email request.'
OBJECT_CREATED_FAILED                   =   'The %(verbose_name)s creation failed: %(reason)s.'
GROUP_JOIN_FAILURE                      =   'Failed to join group.'
GROUPKIND_UNKNOWN                       =   'There is no such a group kind'
NOT_MEMBER                              =   'User is not member of the group.'
NOT_OWNER                               =   'User is not a group owner.'
OWNER_CANNOT_LEAVE_GROUP                =   'Owner cannot leave the group.'

# Field validation fields
REQUIRED_FIELD                          =   'This field is required.'
EMAIL_USED                              =   'This email address is already in use. Please supply a different email address.'
SHIBBOLETH_EMAIL_USED                   =   'This email is already associated with another shibboleth account.'
SHIBBOLETH_INACTIVE_ACC                 =   'This email is already associated with an inactive account. \
                                               You need to wait to be activated before being able to switch to a shibboleth account.'   
SHIBBOLETH_MISSING_EPPN                 =   'Missing unique token in request.'
SHIBBOLETH_MISSING_NAME                 =   'Missing user name in request.'

SIGN_TERMS                              =   'You have to agree with the terms.'
CAPTCHA_VALIDATION_ERR                  =   'You have not entered the correct words.'
SUSPENDED_LOCAL_ACC                     =   'Local login is not the current authentication method for this account.'
UNUSABLE_PASSWORD                       =   'This account has not a usable password.'
EMAIL_UNKNOWN                           =   'That e-mail address doesn\'t have an associated user account. \
                                               Are you sure you\'ve registered?'
INVITATION_EMAIL_EXISTS                 =   'There is already invitation for this email.'
INVITATION_CONSUMED_ERR                 =   'Invitation is used.'
UNKNOWN_USERS                           =   'Unknown users: %s'
UNIQUE_EMAIL_IS_ACTIVE_CONSTRAIN_ERR    =   'Another account with the same email & is_active combination found.'
INVALID_ACTIVATION_KEY                  =   'Invalid activation key.'
NEW_EMAIL_ADDR_RESERVED                 =   'The new email address is reserved.'
EMAIL_RESERVED                          =   'Email: %(email)s is reserved'
NO_LOCAL_AUTH                           =   'Local login is not the current authentication method for this account.'
SWITCH_ACCOUNT_FAILURE                  =   'Account failed to switch. Invalid parameters.'
SWITCH_ACCOUNT_SUCCESS_WITH_PROVIDER    =   'Account failed to switch to %(provider)s.' 
SWITCH_ACCOUNT_SUCCESS                  =   'Account successfully switched to %(provider)s.'

# Field help text
ADD_GROUP_MEMBERS_Q_HELP                =   'Add comma separated user emails, eg. user1@user.com, user2@user.com'
ASTAKOSUSER_GROUPS_HELP                 =   'In addition to the permissions manually assigned, \
                                               this user will also get all permissions granted to each group he/she is in.'
EMAIL_CHANGE_NEW_ADDR_HELP              =   'Your old email address will be used until you verify your new one.'

EMAIL_SEND_ERR                          =   'Failed to send %s.'
ADMIN_NOTIFICATION_SEND_ERR             =   EMAIL_SEND_ERR % 'admin notification'
VERIFICATION_SEND_ERR                   =   EMAIL_SEND_ERR % 'verification'
INVITATION_SEND_ERR                     =   EMAIL_SEND_ERR % 'invitation'
GREETING_SEND_ERR                       =   EMAIL_SEND_ERR % 'greeting'
FEEDBACK_SEND_ERR                       =   EMAIL_SEND_ERR % 'feedback'
CHANGE_EMAIL_SEND_ERR                   =   EMAIL_SEND_ERR % 'feedback'
NOTIFICATION_SEND_ERR                   =   EMAIL_SEND_ERR % 'notification'

MISSING_NEXT_PARAMETER                  =   'No next parameter'

INVITATION_SENT                         =   'Invitation sent to %(email)s.'
VERIFICATION_SENT                       =   'Verification sent.'
SWITCH_ACCOUNT_LINK_SENT                =   'This email is already associated with another local account. \
                                               To change this account to a shibboleth one follow the link in the verification email sent to %(email)s. \
                                               Otherwise just ignore it.'
NOTIFICATION_SENT                       =   'Your request for an account was successfully received and is now pending approval. \
                                               You will be notified by email in the next few days. \
                                               Thanks for your interest in ~okeanos! The GRNET team.'
ACTIVATION_SENT                         =   'Activation sent.'

REGISTRATION_COMPLETED                  =   'Registration completed. You can now login.'

NO_RESPONSE                             =   'There is no response.'
NOT_ALLOWED_NEXT_PARAM                  =   'Not allowed next parameter.'
MISSING_KEY_PARAMETER                   =   'Missing key parameter.'
INVALID_KEY_PARAMETER                   =   'Invalid key.'
