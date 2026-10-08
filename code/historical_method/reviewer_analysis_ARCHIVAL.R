#!/usr/bin/env Rscript
# Independent base-R reproduction of the principal descriptive quantities.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[1] else "."
src <- file.path(root,"outputs","final_q1_release")
out <- file.path(root,"outputs","reviewer_package","r_reproduction")
dir.create(out,recursive=TRUE,showWarnings=FALSE)
orders <- read.csv(file.path(src,"order_level_FINAL_41.csv"),stringsAsFactors=FALSE)
pairs <- read.csv(file.path(src,"linkage_0_1_2_3_9_FINAL_233.csv"),stringsAsFactors=FALSE)
stopifnot(nrow(orders)==41,length(unique(orders$order_id))==41,length(unique(orders$case_number))==27)
stopifnot(nrow(pairs)==233,length(unique(pairs$stage6_pair_key))==233,all(pairs$official_pdf_hash_verified==1))
samples <- list(Primary=orders[orders$primary_sample==1,],Sensitivity=orders[orders$sensitivity_sample==1,])
rows <- list(); j <- 1
for (nm in names(samples)) for (w in c(30,90,180)) {
  d <- samples[[nm]]; k <- sum(d[[paste0("followup_",w,"d")]]); n <- nrow(d)
  ci <- binom.test(k,n)$conf.int
  rows[[j]] <- data.frame(sample=nm,window_days=w,n=n,follow_up=k,rate=k/n,exact_ci_low=ci[1],exact_ci_high=ci[2]); j<-j+1
}
rates <- do.call(rbind,rows); write.csv(rates,file.path(out,"R_follow_up_rates.csv"),row.names=FALSE)
primary <- samples$Primary
tab <- table(factor(primary$reporting_requirement,levels=c("YES","NO")),factor(primary$followup_180d,levels=c(1,0)))
ft <- fisher.test(tab)
writeLines(capture.output(list(contingency_table=tab,fisher_exact=ft)),file.path(out,"R_exact_test.txt"))
pdf(file.path(out,"R_Figure_Follow_Up_Rates.pdf"),width=7,height=4.5)
cols <- c("#17365D","#B07D12"); plot(NA,xlim=c(.7,3.3),ylim=c(0,.40),xaxt="n",xlab="Window",ylab="Order-level follow-through rate",main="Verified institutional follow-through")
axis(1,1:3,c("30 days","90 days","180 days")); abline(h=seq(0,.4,.1),col="#E5E7EB",lty=1)
for (i in 1:2) {d<-rates[rates$sample==names(samples)[i],]; x<-1:3+(i-1.5)*.16; points(x,d$rate,pch=19,col=cols[i]); arrows(x,d$exact_ci_low,x,d$exact_ci_high,angle=90,code=3,length=.04,col=cols[i])}
legend("topright",names(samples),col=cols,pch=19,bty="n")
dev.off()
cat("PASS: R reproduced rates and Fisher exact test\n")
