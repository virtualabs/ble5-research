/**
 * BLE 5 CSA2 PRNG implementation to use with DieHarder
 *
 * (See https://webhome.phy.duke.edu/~rgb/General/dieharder.php)
 *
 * Use this program to generate a file, and then supply it to
 * Dieharder:
 *
 * $ csa2_dieharder > /tmp/buf.bin
 * $ dieharder -g 201 -f /tmp/buf.bin -a -n 2
 * 
 * 
 * This implementation is provided as-is, I'm no cryptographer nor
 * outstanding mathematician (hello @LargeCardinal !), so it may be
 * shit. If it is a shitty code, feel free to tell me why, I would
 * be happy to learn and level up !
 * 
 **/

#include <stdlib.h>
#include <stdio.h>

#define uint16_t unsigned short
#define uint32_t unsigned int

void output_bits(uint16_t data)
{
  printf("%c%c", (unsigned char)(data&0x00ff), (unsigned char)((data&0xff00)>>8));
}

uint16_t channel_id(uint32_t accessAddress)
{
  return ((accessAddress & 0xffff0000)>>16) ^ (accessAddress & 0x0000ffff);
}

uint16_t permute(uint16_t v)
{
  v = (((v & 0xaaaa) >> 1) | ((v & 0x5555) << 1));
  v = (((v & 0xcccc) >> 2) | ((v & 0x3333) << 2));
  return (((v & 0xf0f0) >> 4) | ((v & 0x0f0f) << 4));
}

uint16_t mam(uint16_t a, uint16_t b)
{
  return (17 * a + b) % (0x10000);
}

uint16_t prng(uint16_t counter, uint16_t chanid)
{
  uint16_t prne;

  prne = counter ^ chanid;
  prne = mam(permute(prne), chanid);
  prne = mam(permute(prne), chanid);
  prne = mam(permute(prne), chanid);
  return prne ^ chanid;
}

int main(int argc, char **argv)
{
	int sequence[4096];
	uint16_t cid;
	int diff=0,dble=0,j,k;

	for (cid=0; cid<0xffff; cid++)
	{
		/* Generate sequence */
		for (j=0;j<4096;j++)
			output_bits((uint16_t)prng((uint16_t)j, cid));
		
	}
	return 0;	
}

