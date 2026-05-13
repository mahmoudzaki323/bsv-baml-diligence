test EnterpriseOutageClassifiedCritical {
  functions [ClassifyTicket]
  args {
    ticket #"
      Subject: Production sync failing after v2.8 upgrade
      We upgraded to v2.8 yesterday and our Salesforce sync has been failing since.
      This is blocking reporting for about 40 enterprise customers. Logs show repeated
      auth token refresh errors. We have a renewal call tomorrow and need help ASAP.
    "#
  }
  @@assert({{ this.urgency == "CRITICAL" }})
  @@assert({{ this.needs_human_review == true }})
}

test VagueComplaintNeedsReview {
  functions [ClassifyTicket]
  args {
    ticket #"
      Subject: This is broken again
      Nothing works anymore. Your app keeps doing the same thing as last time and my boss is mad.
      I do not have time to explain this again. Please fix it.
    "#
  }
  @@assert({{ this.category == "UNCLEAR" }})
  @@assert({{ this.needs_human_review == true }})
}

test SecurityReportRoutesSecurity {
  functions [ClassifyTicket]
  args {
    ticket #"
      Subject: Possible tenant data exposure through shared link
      We found that a report link created by one user may be visible to another workspace if the URL is forwarded.
      We have not confirmed data exfiltration, but the behavior looks like cross-tenant access.
    "#
  }
  @@assert({{ this.category == "SECURITY" }})
  @@assert({{ this.team == "SECURITY" }})
}
