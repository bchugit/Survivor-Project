votes <- read.csv("borneo.csv", header=TRUE)
row.names(votes) <- votes$X
votes <- votes[-1]
votes[is.na(votes)] <- 0

m <- as.matrix(votes)
t <- as.table(t(m))

df <- as.data.frame(t)
df <- df[df$Freq != 0,]
df <- df[c(2,1,3)]
colnames(df) <- c("s1", "s2", "samevotes")
View(df)


write.csv(df, "borneoList.csv", row.names=FALSE)


