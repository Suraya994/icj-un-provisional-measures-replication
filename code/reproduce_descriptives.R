#!/usr/bin/env Rscript
# Portable base-R reproduction of core descriptive quantities from package v1.2.0-RC1.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[1] else "."
data <- file.path(root,"data")
out <- file.path(root,"outputs","r_reproduction")
dir.create(out,recursive=TRUE,showWarnings=FALSE)
orders <- read.csv(file.path(data,"05_results","ORDER_LEVEL_RESULTS_41_CANONICAL.csv"),stringsAsFactors=FALSE,check.names=FALSE)
primary <- orders[orders$primary_sample==1,]
sensitivity <- orders[orders$sensitivity_sample==1,]
stopifnot(nrow(orders)==41,nrow(primary)==24,nrow(sensitivity)==27)
rows <- list(); j <- 1
for (nm in c("Primary","Sensitivity")) {
 d <- if (nm=="Primary") primary else sensitivity
 for (w in c(30,90,180)) {
   k <- sum(d[[paste0("order_specific_",w,"d")]])
   n <- nrow(d)
   ci <- binom.test(k,n)$conf.int
   rows[[j]] <- data.frame(sample=nm,window_days=w,n=n,engagement=k,rate=k/n,exact_ci_low=ci[1],exact_ci_high=ci[2]); j<-j+1
 }
}
rates <- do.call(rbind,rows); write.csv(rates,file.path(out,"R_order_specific_rates.csv"),row.names=FALSE)
tab <- table(factor(primary$reporting_requirement,levels=c("YES","NO")),factor(primary$order_specific_engagement_final,levels=c(1,0)))
ft <- fisher.test(tab)
writeLines(capture.output(list(contingency_table=tab,fisher_exact=ft)),file.path(out,"R_reporting_requirement_fisher.txt"))
cat("PASS: R descriptive reproduction completed\n")
