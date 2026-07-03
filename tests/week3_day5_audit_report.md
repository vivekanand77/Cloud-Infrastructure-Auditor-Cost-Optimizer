# Week 3 Day 5 – Scanner Audit Report

## Intern

Nancy Dawani

## Project

Cloud Infrastructure Auditor & Cost Optimizer

---

# Objective

The objective of this week's work was to validate that the AWS resource scanner produces accurate and reliable information before it is used by the resource destruction module.

---

# Resources Verified

The following AWS resources were verified:

- Unattached EBS Volumes
- Unassociated Elastic IP Addresses

---

# Verification Performed

## Week 3 Day 1

Created known AWS test resources using Moto.

Verified that the scanner correctly detected:

- Volume IDs
- Volume Size
- Region
- State
- Elastic IP Allocation ID
- Public IP
- Association Status

Result:

All scanner outputs matched the expected AWS resources.

---

## Week 3 Day 2

Compared each field returned by the scanner against the AWS resources.

Verified:

- Volume ID
- Size
- Region
- State
- Elastic IP Allocation ID
- Public IP
- Association Status

Result:

Every field matched successfully.

No mismatches were observed.

---

## Week 3 Day 3

Reviewed scanner output for possible inconsistencies.

Checked for:

- Incorrect IDs
- Incorrect region
- Incorrect state
- Incorrect attachment status
- Incorrect Elastic IP association

Result:

No logic bugs were found.

No stale or incorrect data was returned.

---

## Week 3 Day 4

Performed edge case testing.

### Edge Case 1

Empty AWS account.

Expected:

No resources returned.

Result:

Passed.

---

### Edge Case 2

Multiple unattached EBS volumes.

Expected:

All volumes detected.

Result:

Passed.

---

### Edge Case 3

Multiple Elastic IPs.

Expected:

All Elastic IPs detected.

Result:

Passed.

---

### Edge Case 4

Mixed resources.

Expected:

Scanner correctly reports both EBS volumes and Elastic IPs.

Result:

Passed.

---

# Summary

| Verification | Status |
|-------------|--------|
| Resource Detection | Passed |
| Field Accuracy | Passed |
| Empty Account | Passed |
| Multiple EBS Volumes | Passed |
| Multiple Elastic IPs | Passed |
| Mixed Resources | Passed |

---

# Findings

No mismatches were found between AWS resources and scanner output.

No crashes occurred during testing.

All expected resources were detected correctly.

---

# Conclusion

The scanner successfully passed all verification tests.

The retrieved AWS resource information is accurate and reliable for further processing.

The scanning module is ready to be used by the destruction module after completing additional integration testing.

---

Prepared By:

Nancy Dawani

Week 3 Internship Submission