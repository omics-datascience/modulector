from modulector.jobs import pubmed_job


# cron job to send emails update to users
def job_caller():
    pubmed_job.execute()
